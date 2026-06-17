#pragma once

struct GpsCoord {
    double lat;
    double lng;
    bool   simulated;
};

void     gps_sim_init(double start_lat, double start_lng,
                      double step_lat,  double step_lng, int steps_turn);
GpsCoord gps_sim_next();
void     gps_sim_override(double lat, double lng);
