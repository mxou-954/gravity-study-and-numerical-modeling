cmake_minimum_required(VERSION 3.16)

project(simulation_gravite LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(simulation_gravite
    main/app.cpp
    tools/csv_tools.cpp
)

target_include_directories(simulation_gravite PRIVATE
    ${CMAKE_SOURCE_DIR}/headers
)