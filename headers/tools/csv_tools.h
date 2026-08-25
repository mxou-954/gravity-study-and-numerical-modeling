#pragma once

#include <iostream>
#include <fstream>
#include <string>

using namespace std;

std::ofstream open_csv_and_verifications(string name);
void close_csv_and_notif(std::ofstream& output, string name);