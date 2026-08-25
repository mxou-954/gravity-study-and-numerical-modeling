#include <iostream>
#include <fstream>
#include <string>

#include "tools/csv_tools.h"

using namespace std;

std::ofstream open_csv_and_verifications(string name){
    std::ofstream output(name);
    if(!output.is_open()){
        std::cerr << "ERREUR: Le fichier " << name << " est impossible a ouvrir !\n";
    }
    return output;
}

void close_csv_and_notif(std::ofstream& output, string name){
    output.close();
    std::cout << "Le fichier de sortie : " << name << " a été généré \n";  
}   