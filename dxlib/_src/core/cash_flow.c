//
// Created by rzimmerdev on 25/11/23.
//
#include <stdlib.h>

#include "cash_flow.h"

int calculate_cash_flow(const int *cash_flow, const int *cash_flow_length, int *sum) {
    *sum = 0;
    for (int i = 0; i < *cash_flow_length; ++i) {
        *sum += cash_flow[i];
    }

    return 0;
}

int minimum_cash_flow(const int *cash_flow, const int *cash_flow_length, int *min) {
    *min = cash_flow[0];
    for (int i = 1; i < *cash_flow_length; ++i) {
        if (cash_flow[i] < *min) {
            *min = cash_flow[i];
        }
    }

    return 0;
}

int maximum_cash_flow(const int *cash_flow, const int *cash_flow_length, int *max) {
    *max = cash_flow[0];
    for (int i = 1; i < *cash_flow_length; ++i) {
        if (cash_flow[i] > *max) {
            *max = cash_flow[i];
        }
    }
    return 0;
}

int cash_flow_with_interest(const int *cash_flow, const int *cash_flow_length, const int *interest_rate, int **cash_flow_with_interest) {
    int *cf = malloc(*cash_flow_length * sizeof(int));
    for (int i = 0; i < *cash_flow_length; ++i) {
        cf[i] = cf[i] * (1 + *interest_rate) + cash_flow[i];
    }

    *cash_flow_with_interest = (int *) cash_flow_with_interest;

    return 0;
}