#define LOG_FMT(LEVEL, ...)                        \
    do                                             \
    {                                              \
        char _buf[256];                            \
        snprintf(_buf, sizeof(_buf), __VA_ARGS__); \
        LOG_##LEVEL(_buf);                         \
    } while (0)