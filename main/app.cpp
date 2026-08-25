#include <iostream>
#include <fstream>
#include <string>
#include <cmath>

#include "constants/constants.hpp"
#include "tools/csv_tools.h"

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
    return ((-4.0/3.0)*Constants::PI*Constants::universal_gravitational_constant*density*density*radius);
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

void study_internal_pressure_without_compression() { // dP/dr

}

int main() {
    study_distance_from_center_effect_inside_uniform_sphere();
}