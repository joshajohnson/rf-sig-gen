#ifndef COMMANDPARSER_H_
#define COMMANDPARSER_H_

extern struct MAX2871Struct max2871Status;
extern struct txStruct txStatus;

void commandParser(struct MAX2871Struct *max2871Status, struct txStruct *txStatus);

#endif
