#include <Arduino.h>
#include <DebugLog.h>
#include "gps_sim.h"
#include "app_helpers.h"

// Directions: 0=N(+lat), 1=E(+lng), 2=S(-lat), 3=W(-lng) — square walking path
static double cur_lat, cur_lng;
static double step_lat, step_lng;
static int    steps_turn;
static int    step_count = 0;
static int    direction  = 0;

static bool   override_active = false;
static double override_lat, override_lng;

void gps_sim_init(double start_lat, double start_lng,
                  double s_lat, double s_lng, int turns) {
    cur_lat    = start_lat;
    cur_lng    = start_lng;
    step_lat   = s_lat;
    step_lng   = s_lng;
    steps_turn = turns;
    step_count = 0;
    direction  = 0;
    override_active = false;
    LOG_FMT(TRACE, "[GPS] Sim initialized: start=(%.6f, %.6f) step=(%.5f, %.5f) turns=%d",
        start_lat, start_lng, s_lat, s_lng, turns);

    // LOG_TRACE("[GPS] Sim initialized: start=(%.6f, %.6f) step=(%.5f, %.5f) turns=%d",
    //           start_lat, start_lng, s_lat, s_lng, turns);

}

void gps_sim_override(double lat, double lng) {
    override_active = true;
    override_lat    = lat;
    override_lng    = lng;
    LOG_FMT(TRACE, "[GPS] Override set: %.6f, %.6f", lat, lng);
    // LOG_TRACE("[GPS] Override set: %.6f, %.6f", lat, lng);
  
}

GpsCoord gps_sim_next() {
    if (override_active) {
        return {override_lat, override_lng, true};
    }

    GpsCoord pos = {cur_lat, cur_lng, true};

    switch (direction % 4) {
        case 0: cur_lat += step_lat; break;
        case 1: cur_lng += step_lng; break;
        case 2: cur_lat -= step_lat; break;
        case 3: cur_lng -= step_lng; break;
    }

    if (++step_count >= steps_turn) {
        step_count = 0;
        direction  = (direction + 1) % 4;
    }

    return pos;
}
