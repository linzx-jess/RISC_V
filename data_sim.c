#include <stdio.h>
#include <stdlib.h>

void delay_ms(volatile unsigned int ms) {
    volatile unsigned int i, j;
    const unsigned int LOOPS = 10000000; 
    for (i = 0; i < LOOPS; i++) {
    }
}

void generate_data(float *temp, float *humid) {
    *temp = 20.0 + (float)rand() / (float)(RAND_MAX / 10.0);
    *humid = 50.0 + (float)rand() / (float)(RAND_MAX / 20.0);
}

int main() {
    float temperature, humidity;
    srand(1); 
    puts("RISC-V IoT Data Simulator Starting...\n"); 
    while (1) {
        generate_data(&temperature, &humidity);
        printf("T:%.1f,H:%.1f\n", temperature, humidity);
        fflush(stdout); 
        delay_ms(1);
    }

    return 0;
}