export type User = {
  id: string;
  name: string;
  email: string;
  college?: string;
  year?: string;
  branch?: string;
  phone?: string;
  verified?: boolean;
  rating?: number;
  trust_score?: number;
};

export type Ride = {
  ride_id: string;
  origin: { lat?: number; lon?: number; name?: string };
  departure_time: string;
  seats_left: number;
  vehicle_name: string;
  distance_from_you?: number;
  fare?: { passenger_pays?: number; breakdown?: string };
  rider?: { name?: string; rating?: number; year?: string; branch?: string; verified?: boolean };
};

export type RequestItem = {
  request_id: string;
  status: string;
  fare: { passenger_pays?: number };
  ride: { departure_time?: string; origin?: { name?: string } };
  rider?: { name?: string; phone?: string; vehicle?: string }; 
};
