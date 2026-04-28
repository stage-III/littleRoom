import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import RoomsGrid from '../islands/RoomsGrid.svelte';
import type { Room } from '../lib/api';

vi.mock('../lib/api', () => ({
  api: { get: vi.fn() },
}));

import { api } from '../lib/api';

const mockRooms: Room[] = [
  {
    id: 1,
    name: 'Room A',
    slug: 'room-a',
    description: 'A great room for bands',
    size_sqm: 20,
    hourly_rate: '15.00',
    equipment: [{ id: 1, name: 'Drum kit' }, { id: 2, name: 'Bass amp' }],
  },
];

describe('RoomsGrid', () => {
  beforeEach(() => vi.clearAllMocks());

  it('shows loading state initially', () => {
    vi.mocked(api.get).mockReturnValue(new Promise(() => {}));
    render(RoomsGrid);
    expect(screen.getByText(/loading rooms/i)).toBeInTheDocument();
  });

  it('renders a card for each room after loading', async () => {
    vi.mocked(api.get).mockResolvedValue(mockRooms);
    render(RoomsGrid);
    await waitFor(() => expect(screen.getByText('Room A')).toBeInTheDocument());
  });

  it('shows the hourly rate', async () => {
    vi.mocked(api.get).mockResolvedValue(mockRooms);
    render(RoomsGrid);
    await waitFor(() => expect(screen.getByText(/£15\.00 \/ hr/)).toBeInTheDocument());
  });

  it('renders equipment items', async () => {
    vi.mocked(api.get).mockResolvedValue(mockRooms);
    render(RoomsGrid);
    await waitFor(() => {
      expect(screen.getByText('Drum kit')).toBeInTheDocument();
      expect(screen.getByText('Bass amp')).toBeInTheDocument();
    });
  });

  it('shows empty message when no rooms are returned', async () => {
    vi.mocked(api.get).mockResolvedValue([]);
    render(RoomsGrid);
    await waitFor(() => expect(screen.getByText(/no rooms listed yet/i)).toBeInTheDocument());
  });

  it('shows error message when the fetch fails', async () => {
    vi.mocked(api.get).mockRejectedValue(new Error('Network error'));
    render(RoomsGrid);
    await waitFor(() => expect(screen.getByText(/could not load rooms/i)).toBeInTheDocument());
  });
});
