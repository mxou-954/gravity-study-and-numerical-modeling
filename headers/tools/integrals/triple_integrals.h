#pragma once
#include <iostream>
#include <functional>

double integrale3d(std::function<double(double, double, double)> f, double ax, double bx, double ay, double by, double az, double bz, int n = 10000);