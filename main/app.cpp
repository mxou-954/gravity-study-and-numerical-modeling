#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <vector>

#include "constants/constants.hpp"
#include "tools/csv_tools.h"
#include "layer/layer.h"
#include "tools/integrals/simple_integrals.h"
#include "tools/integrals/double_integrals.h"
#include "tools/integrals/triple_integrals.h"

using namespace std;

// CALCULATION FUNCTIONS

double gravitational_field_formula(
    double celestial_body_mass, 
    double radius
) { // La masse est en kg et le rayon en mètres
    return (Constants::universal_gravitational_constant*celestial_body_mass)/(radius*radius);
}

double gravitational_field_radius(
    double celestial_body_mass, 
    double gravity_min
) {
    return std::sqrt((Constants::universal_gravitational_constant*celestial_body_mass)/(gravity_min));
}

double mass_from_radius_and_density(
    double radius, 
    double density
) { // R en m, Rho en kg/m^3 et M en kg
    return (4.0/3.0*Constants::PI*(radius*radius*radius)*density);
}

double density_from_mass_and_radius(
    double radius, 
    double mass
) {
    return ((mass)/((4.0/3.0)*Constants::PI*(radius*radius*radius)));
}

double radius_from_mass_and_density(
    double mass, 
    double density
) {
    return (std::cbrt((mass)/((4.0/3.0)*Constants::PI*density)));
}

double gravitational_field_outside_uniform_sphere(
    double density,
    double radius,
    double distance_from_center
) {
    return (4.0 * Constants::PI * Constants::universal_gravitational_constant / 3.0)
        * density
        * radius * radius * radius
        / (distance_from_center * distance_from_center);
}

double gravitational_field_inside_uniform_sphere(
    double density,
    double distance_from_center
) {
    return (4.0 * Constants::PI * Constants::universal_gravitational_constant / 3.0)
        * density
        * distance_from_center * distance_from_center * distance_from_center
        / (distance_from_center * distance_from_center);
}

double internal_pressure_without_compression(
    double density, 
    double radius
) {
    return ( (-4.0/3.0)
    * Constants::PI * Constants::universal_gravitational_constant
    * density * density * radius);
}

double mass_from_delta_radius_and_density(double r1, double r2, double density) { // delta mass
    return ((4.0/3.0)
    * Constants::PI
    * ((r1*r1*r1)-(r2*r2*r2))
    * density);
}

double volume_from_delta_radius(double r1, double r2) { // delta volume
    return ((4.0/3.0)
    * Constants::PI
    * ((r1*r1*r1)-(r2*r2*r2)));
}

std::vector<Layer> earth_layers = {
        {0.0,       1221500.0, 12893.6, Constants::test_bulk_modulus},
        {1221500.0, 3480000.0, 10900.7, Constants::test_bulk_modulus},
        {3480000.0, 5701000.0, 4903.58, Constants::test_bulk_modulus},
        {5701000.0, 5771000.0, 3983.94, Constants::test_bulk_modulus},
        {5771000.0, 5971000.0, 3848.35, Constants::test_bulk_modulus},
        {5971000.0, 6151000.0, 3488.99, Constants::test_bulk_modulus},
        {6151000.0, 6291000.0, 3367.16, Constants::test_bulk_modulus},
        {6291000.0, 6346600.0, 3377.74, Constants::test_bulk_modulus},
        {6346600.0, 6356000.0, 2900.00, Constants::test_bulk_modulus},
        {6356000.0, 6368000.0, 2600.00, Constants::test_bulk_modulus},
        {6368000.0, Constants::earth_radius, 1020.00, Constants::test_bulk_modulus}
};

double define_density(double radius){
    
    for(int i = 0; i < earth_layers.size(); i++){
        if(radius >= earth_layers[i].inner_radius && radius <= earth_layers[i].outer_radius){
            return earth_layers[i].density;
        }
    }
}

double delta_V_with_K(double radius, double delta_P, double V_old) {
    for(int i =0; i <= earth_layers.size(); i++){
        if(radius >= earth_layers[i].inner_radius && radius <= earth_layers[i].outer_radius){
            return -(V_old/earth_layers[i].bulk_modulus)*delta_P;
        }
    }
}

// STUDIES

void study_mass_increase() { // 1kg * 1,001 => 1000 fois
    std::ofstream output = open_csv_and_verifications("../data/study_mass_increase");

    output << "celestial_body_mass,radius,gravitational_field\n";
    for(double i = 1.0; i<= 1.0e300; i*=1.001){
        double result = gravitational_field_formula(i, Constants::earth_radius);
        output << i << "," << Constants::earth_radius << "," << result << "\n";
    };
    
    close_csv_and_notif(output, "study_mass_increase");
}

void study_mass_decrease() {
    std::ofstream output = open_csv_and_verifications("../data/study_mass_decrease");

    output << "celestial_body_mass,radius,gravitational_field\n";
    for(double i = 1.0; i>= 1.0e-300; i/=1.001){
        double result = gravitational_field_formula(i, Constants::earth_radius);
        output << i << "," << Constants::earth_radius << "," << result << "\n";
    };
    
    close_csv_and_notif(output, "study_mass_decrease");
}

void study_radius_increase() {
    std::ofstream output = open_csv_and_verifications("../data/study_radius_increase");

    output << "celestial_body_mass,radius,gravitational_field\n";
    for(double i = 1.0; i<= 1.0e300; i*=1.001){
        double result = gravitational_field_formula(Constants::earth_mass, i);
        output << Constants::earth_mass << "," << i << "," << result << "\n";
    };
    
    close_csv_and_notif(output, "study_radius_increase");
}

void study_radius_decrease() {
    std::ofstream output = open_csv_and_verifications("../data/study_radius_decrease");

    output << "celestial_body_mass,radius,gravitational_field\n";
    for(double i = 1.0; i>= 1.0e-300; i/=1.001){
        double result = gravitational_field_formula(Constants::earth_mass, i);
        output << Constants::earth_mass << "," << i << "," << result << "\n";
    };
    
    close_csv_and_notif(output, "study_radius_decrease");
}

void study_gravitational_radius() {
    std::ofstream output = open_csv_and_verifications("../data/study_gravitational_radius");

    output << "celestial_body_mass,minimum_gravity,gravitational_radius\n";
    for (double i = 0.001; i <= 1.0e300; i *= 1.001) {
        double result = gravitational_field_radius(i, 0.001);
        output << i << "," << 0.001 << "," << result << "\n";
    }
    
    close_csv_and_notif(output, "study_gravitational_radius");
}

void study_constant_density_incremented_radius() {
    std::ofstream output = open_csv_and_verifications("../data/study_constant_density_incremented_radius");

    output << "radius,density,mass\n";
    for (double i = 0.001; i <= 1.0e300 && i >= 1.0e-300; i *= 1.001) {
        double result = mass_from_radius_and_density(i, Constants::earth_average_density);
        output << i << "," << Constants::earth_average_density << "," << result << "\n";
    }
    
    close_csv_and_notif(output, "study_constant_density_incremented_radius");
}

void study_constant_mass_incremented_radius() {
    std::ofstream output = open_csv_and_verifications("../data/study_constant_mass_incremented_radius");

    output << "radius,mass,density\n";
    for (double i = 0.001; i <= 1.0e300 && i >= 1.0e-300; i *= 1.001) {
        double result = density_from_mass_and_radius(i, Constants::earth_mass);
        output << i << "," << Constants::earth_mass << "," << result << "\n";
    }
    
    close_csv_and_notif(output, "study_constant_mass_incremented_radius");
}

void study_density_effect_on_gravity(){
    std::ofstream output = open_csv_and_verifications("../data/study_density_effect_on_gravity");

    output << "radius,distance_from_center,density,gravitational_field\n";
    for (double i = 0.001; i <= 1.0e300 && i >= 1.0e-300; i *= 1.001) {
        double result = gravitational_field_outside_uniform_sphere(i, Constants::earth_radius, Constants::earth_radius);
        output << Constants::earth_radius << "," << Constants::earth_radius << "," << i << "," << result << "\n";
    }
    
    close_csv_and_notif(output, "study_density_effect_on_gravity");
}

void study_radius_effect_on_surface_gravity_constant_density() {
    std::ofstream output = open_csv_and_verifications("../data/study_radius_effect_on_surface_gravity_constant_density");

    output << "radius,distance_from_center,density,gravitational_field\n";
    for (double i = 0.001; i <= 1.0e300 && i >= 1.0e-300; i *= 1.001) {
        double result = gravitational_field_outside_uniform_sphere(Constants::earth_average_density, i, i);
        output << i << "," << i << "," << Constants::earth_average_density << "," << result << "\n";
    }
    
    close_csv_and_notif(output, "study_radius_effect_on_surface_gravity_constant_density"); 
}

void study_density_effect_on_surface_gravity_constant_mass() {
    std::ofstream output = open_csv_and_verifications("../data/study_density_effect_on_surface_gravity_constant_mass");

    output << "earth_mass,radius,distance_from_center,density,gravitational_field\n";
    for (double i = 0.001; i <= 1.0e300 && i >= 1.0e-300; i *= 1.001) { // i = density
        double radius = radius_from_mass_and_density(Constants::earth_mass, i);
        double result = gravitational_field_outside_uniform_sphere(i, radius, radius);
        output << Constants::earth_mass << "," << radius << "," << radius << "," << i << "," << result << "\n";
    }
    
    close_csv_and_notif(output, "study_density_effect_on_surface_gravity_constant_mass"); 
}

void study_distance_from_center_effect_inside_uniform_sphere() {
    std::ofstream output = open_csv_and_verifications("../data/study_distance_from_center_effect_inside_uniform_sphere");

    output << "distance_from_center,enclosed_mass,gravitational_field\n";
    for (double i = 0.001; i <= Constants::earth_radius; i *= 1.001) {
        double enclosed_mass = mass_from_radius_and_density(i, Constants::earth_average_density);
        double result = gravitational_field_inside_uniform_sphere(Constants::earth_average_density, i);

        output << i << "," << enclosed_mass << "," << result << "\n";
    }
    
    close_csv_and_notif(output, "study_distance_from_center_effect_inside_uniform_sphere"); 
}

void study_internal_pressure_without_compression() { // dP/dr => dP/dr * dr => dP
    std::ofstream output = open_csv_and_verifications("../data/study_internal_pressure_without_compression");

    output << "density,radius,dP/dr,delta_r,delta_P,pressure\n";

    double pressure = 0;
    double prev_r = Constants::earth_radius;
    for (double i = Constants::earth_radius; i > 0.001; i /= 1.001) {
        
        double result = internal_pressure_without_compression(Constants::earth_average_density, i);
        double delta_r = i - prev_r;
        double delta_P = result * delta_r;
        pressure += delta_P;

        output << Constants::earth_average_density << "," << i << "," << result << "," << delta_r << "," << delta_P << "," << pressure << "\n";
        prev_r = i;
    }
    
    close_csv_and_notif(output, "study_internal_pressure_without_compression");
}

void study_internal_pressure_without_compression_layer_by_layer() { // dP/dr => dP/dr * dr => dP
    std::ofstream output = open_csv_and_verifications("../data/study_internal_pressure_without_compression_layer_by_layer");

    output << "radius,density,delta_mass,outside_mass,enclosed_mass,gravitational_field,dP/dr,delta_r,delta_P,pressure\n";

    double prev_r = Constants::earth_radius;
    double total_mass = 0;
    for (double i = Constants::earth_radius; i > 0.001; i /= 1.001) {
        
        double density = (i <= Constants::earth_radius/2) 
            ? Constants::earth_average_density/2
            : Constants::earth_average_density;

        double delta_mass = mass_from_delta_radius_and_density(prev_r, i, density);
        total_mass += delta_mass;

        prev_r = i;
    };

    prev_r = Constants::earth_radius;
    double pressure = 0;
    double outside_mass = 0;
    double enclosed_mass = 0;
    for (double i = Constants::earth_radius; i > 0.001; i /= 1.001) {
        
        double density = (i <= Constants::earth_radius/2) 
            ? Constants::earth_average_density/2
            : Constants::earth_average_density;

        double delta_mass = mass_from_delta_radius_and_density(prev_r, i, density);
        outside_mass += delta_mass;
        enclosed_mass = total_mass - outside_mass;
        double gravitational_field = gravitational_field_formula(enclosed_mass, i);
        double dP_dr = (-density)*gravitational_field;
        double delta_r = i - prev_r;
        double delta_P = dP_dr * delta_r;
        pressure += delta_P;

        prev_r = i;
        output << i << "," << density << "," << delta_mass << "," << outside_mass << "," <<
        enclosed_mass << "," << gravitational_field << "," << dP_dr << "," <<
        delta_r << "," << delta_P << "," << pressure << "\n";
    }

    close_csv_and_notif(output, "study_internal_pressure_without_compression_layer_by_layer");
}

void study_internal_pressure_without_compression_layer_by_layer_PREM() { // dP/dr => dP/dr * dr => dP
    std::ofstream output = open_csv_and_verifications("../data/study_internal_pressure_without_compression_layer_by_layer_PREM");

    output << "radius,density,delta_mass,outside_mass,enclosed_mass,gravitational_field,dP/dr,delta_r,delta_P,pressure\n";

    double prev_r = Constants::earth_radius;
    double total_mass = 0;
    for (double i = Constants::earth_radius; i > 0.0001; i /= 1.0001) {
        
        double density = define_density(i);

        double delta_mass = mass_from_delta_radius_and_density(prev_r, i, density);
        total_mass += delta_mass;

        prev_r = i;
    };

    prev_r = Constants::earth_radius;
    double pressure = 0;
    double outside_mass = 0;
    double enclosed_mass = 0;
    for (double i = Constants::earth_radius; i > 0.0001; i /= 1.0001) {
        
        double density = define_density(i);

        double delta_mass = mass_from_delta_radius_and_density(prev_r, i, density);
        outside_mass += delta_mass;
        enclosed_mass = total_mass - outside_mass;
        double gravitational_field = gravitational_field_formula(enclosed_mass, i);
        double dP_dr = (-density)*gravitational_field;
        double delta_r = i - prev_r;
        double delta_P = dP_dr * delta_r;
        pressure += delta_P;

        prev_r = i;
        output << i << "," << density << "," << delta_mass << "," << outside_mass << "," <<
        enclosed_mass << "," << gravitational_field << "," << dP_dr << "," <<
        delta_r << "," << delta_P << "," << pressure << "\n";
    }

    close_csv_and_notif(output, "study_internal_pressure_without_compression_layer_by_layer_PREM");
}

void study_internal_pressure_with_compression_layer_by_layer_PREM() { // dP/dr => dP/dr * dr => dP
    std::ofstream output = open_csv_and_verifications("../data/study_internal_pressure_with_compression_layer_by_layer_PREM");

    output << "radius,density,delta_mass,outside_mass,enclosed_mass,gravitational_field,dP/dr,delta_r,delta_P,pressure,pressure_before,pressure_shell,V_old,total_volume,delta_V,V_new,new_density\n";

    double prev_r = Constants::earth_radius;
    double total_mass = 0;
    double total_volume = 0;
    for (double i = Constants::earth_radius/0.0001; i > 0.0001; i /= 1.0001) {
        
        double density = define_density(i);

        double delta_mass = mass_from_delta_radius_and_density(prev_r, i, density);
        total_mass += delta_mass;

        prev_r = i;
    };

    prev_r = Constants::earth_radius;
    double pressure = 0;
    double outside_mass = 0;
    double enclosed_mass = 0;
    for (double i = Constants::earth_radius/0.0001; i > 0.0001; i /= 1.0001) {
        
        double density = define_density(i);

        double delta_mass = mass_from_delta_radius_and_density(prev_r, i, density);
        outside_mass += delta_mass;
        enclosed_mass = total_mass - outside_mass;
        double gravitational_field = gravitational_field_formula(enclosed_mass, i);
        double dP_dr = (-density)*gravitational_field;
        double delta_r = i - prev_r;

        double pressure_before = pressure;
        double delta_P = dP_dr * delta_r;
        pressure += delta_P;

        double pressure_shell = pressure_before + delta_P / 2.0;

        double V_old = volume_from_delta_radius(prev_r, i);
        total_volume += V_old;

        double delta_V = delta_V_with_K(i, pressure_shell, V_old); 
        double V_new = V_old + delta_V; 
        double new_density = delta_mass/V_new;

        prev_r = i;
        output << i << "," << density << "," << delta_mass << "," << outside_mass << "," <<
        enclosed_mass << "," << gravitational_field << "," << dP_dr << "," <<
        delta_r << "," << delta_P << "," << pressure << "," << pressure_before << "," << 
        pressure_shell << "," << V_old << "," << total_volume << "," << delta_V << "," << V_new << "," << new_density << "\n";
    }

    close_csv_and_notif(output, "study_internal_pressure_with_compression_layer_by_layer_PREM");
}

int main() {
    auto f = [](double x, double y, double z) {
        return 2*x*x*x + 3*y*y - 4*z;
    };

    double r = integrale3d(f, 0, 1, 0, 1, 0, 1, 1);
    std::cout << r << "\n";   // 0.5
}