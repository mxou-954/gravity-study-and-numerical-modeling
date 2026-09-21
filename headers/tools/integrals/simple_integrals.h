#pragma once
#include <iostream>
#include <functional>

double integrale1d(std::function<double(double)> f, double a, double b, int n = 10000);