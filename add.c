#include <stdio.h>

int main()
{
	int x,sum,T_0;
	L_1: 
	L_2: scanf("%d",&x); //(inp x _ _)
	L_3: sum=0; //(:= 0 _ sum)
	L_4: if (x>0) goto L_6; //(> x 0 6)
	L_5: goto L_9; //(jump _ _ 9)
	L_6: T_0=sum+x; //(+ sum x T_0)
	L_7: sum=T_0; //(:= T_0 _ sum)
	L_8: goto L_4; //(jump _ _ 4)
	L_9: printf("%d",sum); //(out sum _ _)
	L_10: 
	L_11: 
}