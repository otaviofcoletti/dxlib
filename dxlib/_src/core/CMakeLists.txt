add_library(dxlib STATIC portfolio.c)

target_include_directories(dxlib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})