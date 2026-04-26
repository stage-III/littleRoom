<script lang="ts">
  import { api, type AvailabilityResponse, type AvailableRoom, type Booking, type Slot, type StudioSettings } from '../lib/api';
  import StepDate from './StepDate.svelte';
  import StepRoom from './StepRoom.svelte';
  import StepSlot from './StepSlot.svelte';
  import StepPayment from './StepPayment.svelte';
  import StepConfirmation from './StepConfirmation.svelte';

  type Step = 'date' | 'room' | 'slot' | 'payment' | 'confirmation';
  const STEPS: { key: Step; label: string }[] = [
    { key: 'date',    label: 'Date' },
    { key: 'room',    label: 'Room' },
    { key: 'slot',    label: 'Time' },
    { key: 'payment', label: 'Confirm' },
  ];

  let step: Step = $state('date');
  let settings = $state<StudioSettings | null>(null);
  let selectedDate: string = $state('');
  let availability: AvailabilityResponse | null = $state(null);
  let selectedRoom: AvailableRoom | null = $state(null);
  let selectedSlot: Slot | null = $state(null);
  let durationHours: number = $state(0);
  let createdBooking: Booking | null = $state(null);
  let submitting: boolean = $state(false);
  let submitError: string = $state('');

  const isLoggedIn = typeof localStorage !== 'undefined' && !!localStorage.getItem('token');

  function today(): string {
    return new Date().toLocaleDateString('en-CA'); // YYYY-MM-DD
  }

  function addDays(date: string, days: number): string {
    const d = new Date(date);
    d.setDate(d.getDate() + days);
    return d.toLocaleDateString('en-CA');
  }

  const minDate = $derived(addDays(today(), settings?.min_notice_days ?? 0));

  $effect(() => {
    api.get<StudioSettings>('/settings/').then(s => { settings = s; }).catch(() => {});
  });

  function stepIndex(s: Step): number {
    return STEPS.findIndex(x => x.key === s);
  }

  const currentStepIndex = $derived(stepIndex(step));

  function handleDateConfirm(date: string, avail: AvailabilityResponse) {
    selectedDate = date;
    availability = avail;
    step = 'room';
  }

  function handleRoomConfirm(room: AvailableRoom) {
    selectedRoom = room;
    step = 'slot';
  }

  function handleSlotConfirm(slot: Slot, hours: number) {
    selectedSlot = slot;
    durationHours = hours;
    submitError = '';
    step = 'payment';
  }

  async function handlePaymentConfirm(paymentMethod: string, guestEmail: string, guestName: string) {
    submitting = true;
    submitError = '';
    try {
      const start = selectedSlot!.start_time;
      const end = new Date(new Date(start).getTime() + durationHours * 3_600_000).toISOString();
      const payload: Record<string, unknown> = {
        room: selectedRoom!.room_id,
        start_datetime: start,
        end_datetime: end,
        payment_method: paymentMethod,
      };
      if (guestEmail) payload.guest_email = guestEmail;
      if (guestName)  payload.guest_name  = guestName;

      const booking = await api.post<Booking>('/bookings/', payload);
      createdBooking = booking;
      step = 'confirmation';
    } catch (err: unknown) {
      const apiErr = err as { data?: { non_field_errors?: string[]; detail?: string } };
      submitError =
        apiErr.data?.non_field_errors?.[0] ??
        apiErr.data?.detail ??
        'Could not complete booking. Please try again.';
    } finally {
      submitting = false;
    }
  }

  function goBack() {
    submitError = '';
    if      (step === 'room')    step = 'date';
    else if (step === 'slot')    step = 'room';
    else if (step === 'payment') step = 'slot';
  }
</script>

<div class="booking-flow">
  {#if step !== 'confirmation'}
    <nav class="progress" aria-label="Booking steps">
      {#each STEPS as s, i}
        <span
          class="progress-step"
          class:active={s.key === step}
          class:done={i < currentStepIndex}
        >{s.label}</span>
        {#if i < STEPS.length - 1}
          <span class="progress-sep">›</span>
        {/if}
      {/each}
    </nav>
  {/if}

  {#if step === 'date' && settings}
    <StepDate
      initialDate={selectedDate}
      {minDate}
      onConfirm={handleDateConfirm}
    />
  {:else if step === 'room' && availability}
    <StepRoom
      {availability}
      onConfirm={handleRoomConfirm}
      onBack={goBack}
    />
  {:else if step === 'slot' && selectedRoom && availability}
    <StepSlot
      room={selectedRoom}
      minBookingHours={availability.min_booking_hours ?? 1}
      onConfirm={handleSlotConfirm}
      onBack={goBack}
    />
  {:else if step === 'payment' && selectedRoom && selectedSlot}
    <StepPayment
      room={selectedRoom}
      slot={selectedSlot}
      {durationHours}
      {isLoggedIn}
      {submitting}
      error={submitError}
      onConfirm={handlePaymentConfirm}
      onBack={goBack}
    />
  {:else if step === 'confirmation' && createdBooking}
    <StepConfirmation
      booking={createdBooking}
      {isLoggedIn}
    />
  {/if}
</div>

<style>
  .booking-flow {
    max-width: 560px;
  }

  .progress {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    margin-bottom: 2rem;
    font-size: 0.8rem;
  }

  .progress-step {
    color: #bbb;
    font-weight: 500;
  }

  .progress-step.done { color: #888; }
  .progress-step.active { color: #1a1a1a; font-weight: 600; }

  .progress-sep { color: #ccc; font-size: 0.75rem; }
</style>
