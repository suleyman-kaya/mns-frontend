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
    CAN_Cihazi() {
        output.reset();
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

// Test zamanııı :))
int main() {
    CAN_Cihazi can_cihazi;

    // Örnek test verileri
    can_cihazi.output = std::bitset<5>("10101");  // 21

    std::cout << "CAN_Cihazi output: " << can_cihazi.output << std::endl;
    std::cout << "CAN_Cihazi get_output1: " << can_cihazi.get_output1() << std::endl;
    std::cout << "CAN_Cihazi get_output2: " << can_cihazi.get_output2() << std::endl;

    Sonuc = Bitwise_Sum(can_cihazi.get_output1().to_ullong(), can_cihazi.get_output2().to_ullong());

    std::cout << "Result Bitwise_Sum (Sonuc): " << Sonuc << std::endl;

    return 0;
}