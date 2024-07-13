#include <iostream>
#include <string>
#include <vector>
#include <bitset>
#include <cstdint>

template<size_t M>
uint64_t extract_bits(uint64_t input, int start, int end) {
    uint64_t mask = ((1ULL << (end - start + 1)) - 1) << start;
    return (input & mask) >> start;
}

class CAN_Cihazi {
public:
    std::bitset<5> output;
    std::string id;
    bool isStd;
    CAN_Cihazi() {
        output.reset();
        id = "d5a1f8";
        isStd = false;
    }
    std::bitset<3> get_output1() const {
        return extract_bits<3>(output.to_ullong(), 0, 2);
    }
    std::bitset<3> get_output2() const {
        return extract_bits<3>(output.to_ullong(), 2, 4);
    }
};

uint64_t Bitwise_Sum(uint64_t input1, uint64_t input2) {
    uint64_t output1 = input1 + input2;
    return output1;
}

uint64_t Sonuc;

int main() {
    CAN_Cihazi can_cihazi;
    can_cihazi.output = std::bitset<5>("11000");

    std::cout << "CAN_Cihazi ID: " << can_cihazi.id << "\n" ;
    std::cout << "ID (1->STD    0->EXTD): " << can_cihazi.isStd << "\n" ;
    std::cout << "CAN_Cihazi Veri Çıkışı: " << can_cihazi.output << "\n";
    std::cout << "CAN_Cihazi Output Pin 1: " << can_cihazi.get_output1() << "\n";
    std::cout << "CAN_Cihazi Output Pin 2: " << can_cihazi.get_output2() << "\n";

    Sonuc = Bitwise_Sum(can_cihazi.get_output1().to_ullong(), can_cihazi.get_output2().to_ullong());
    std::cout << "Bitwise_Sum sonucu: " << Sonuc << "\n";

    std::cout << "Sonuc değişkeninin değeri: " << Sonuc << "\n";

    return 0;
}
