//
// Created by rzimmerdev on 25/11/23.
//

#ifndef DXLIB_TEST_CASH_FLOW_H
#define DXLIB_TEST_CASH_FLOW_H

int calculate_cash_flow(const int *cash_flow, const int *cash_flow_length, int *sum);

int minimum_cash_flow(const int *cash_flow, const int *cash_flow_length, int *min);

int maximum_cash_flow(const int *cash_flow, const int *cash_flow_length, int *max);

int cash_flow_with_interest(const int *cash_flow, const int *cash_flow_length, const int *interest_rate, int **cash_flow_with_interest);

#endif //DXLIB_TEST_CASH_FLOW_H
