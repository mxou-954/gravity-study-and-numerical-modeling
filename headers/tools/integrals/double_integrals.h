#pragma once
#include <iostream>
#include <functional>

double integrale2d(std::function<double(double, double)> f, double ax, double bx, double ay, double by, int n = 10000);