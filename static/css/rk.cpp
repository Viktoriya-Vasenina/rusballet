#include <iostream>

int main() {
    double num1, num2;
    char operation;
    
    std::cout << "=== Калькулятор ===\n";
    std::cout << "Введите операцию (+, -, *, /): ";
    std::cin >> operation;
    
    std::cout << "Введите два числа: ";
    std::cin >> num1 >> num2;
    
    switch(operation) {
        case '+':
            std::cout << num1 << " + " << num2 << " = " << num1 + num2 << std::endl;
            break;
        case '-':
            std::cout << num1 << " - " << num2 << " = " << num1 - num2 << std::endl;
            break;
        case '*':
            std::cout << num1 << " * " << num2 << " = " << num1 * num2 << std::endl;
            break;
        case '/':
            if (num2 != 0) {
                std::cout << num1 << " / " << num2 << " = " << num1 / num2 << std::endl;
            } else {
                std::cout << "Ошибка: деление на ноль!" << std::endl;
            }
            break;
        default:
            std::cout << "Ошибка: неизвестная операция!" << std::endl;
    }
    
    return 0;
}
