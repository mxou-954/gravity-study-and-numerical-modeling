// triple_integrals.cpp
#include "tools/integrals/simple_integrals.h"
#include "tools/integrals/triple_integrals.h"

double integrale3d(std::function<double(double, double, double)> f,
                   double ax, double bx, double ay, double by,
                   double az, double bz, int n) {
    return integrale1d([&](double x) {
        std::cout << "  x = " << x << "\n";
        return integrale1d([&, x](double y) {
            std::cout << "    y = " << y << "\n";
            return integrale1d([&, x, y](double z) {
                std::cout << "      f(" << x << "," << y << "," << z << ")\n";
                return f(x, y, z);
            }, az, bz, n);
        }, ay, by, n);
    }, ax, bx, n);
}