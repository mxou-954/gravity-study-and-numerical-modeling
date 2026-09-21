// double_integrals.cpp
#include "tools/integrals/simple_integrals.h"
#include "tools/integrals/double_integrals.h"

double integrale2d(std::function<double(double, double)> f,
                   double ax, double bx, double ay, double by, int n) {
    return integrale1d([&](double x) {
        return integrale1d([&, x](double y) { return f(x, y); }, ay, by, n);
    }, ax, bx, n);
}