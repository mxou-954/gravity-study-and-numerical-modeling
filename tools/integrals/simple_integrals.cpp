// simple_integrals.cpp
#include "tools/integrals/simple_integrals.h"

double integrale1d(std::function<double(double)> f, double a, double b, int n)
{
    n += n % 2;
    double h = (b - a) / n;
    double s = f(a) + f(b);
    for (int i = 1; i < n; ++i)
        s += f(a + i * h) * (i % 2 ? 4.0 : 2.0);
    return s * h / 3.0;
}