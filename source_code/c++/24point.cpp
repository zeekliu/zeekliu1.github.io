#include<bits/stdc++.h>
using namespace std;
bool check(double x){
	return round(x*16384)==393216;//24*16384
}
bool _3(double a,double b){
	return check(a+b)||
		   check(a-b)||
		   check(a*b)||
		   check(a/b)||
		   check(b-a)||
		   check(b/a);
}
bool _2(double a,double b,double c){
	return _3(a+b,c)||
		   _3(a-b,c)||
		   _3(b-a,c)||
		   _3(a*b,c)||
		   _3(a/b,c)||
		   _3(b/a,c)||
		   _3(a+c,b)||
		   _3(a-c,b)||
		   _3(c-a,b)||
		   _3(a*c,b)||
		   _3(a/c,b)||
		   _3(c/a,b)||
		   _3(b+c,a)||
		   _3(b-c,a)||
		   _3(c-b,a)||
		   _3(b*c,a)||
		   _3(b/c,a)||
		   _3(c/b,a);
}
bool _1(double a,double b,double c,double d){
	return _2(a+b,c,d)||
		   _2(a-b,c,d)||
		   _2(b-a,c,d)||
		   _2(a*b,c,d)||
		   _2(a/b,c,d)||
		   _2(b/a,c,d)||
		   _2(a+c,b,d)||
		   _2(a-c,b,d)||
		   _2(c-a,b,d)||
		   _2(a*c,b,d)||
		   _2(a/c,b,d)||
		   _2(c/a,b,d)||
		   _2(a+d,b,c)||
		   _2(a-d,b,c)||
		   _2(d-a,b,c)||
		   _2(a*d,b,c)||
		   _2(a/d,b,c)||
		   _2(d/a,b,c)||
		   _2(b+c,a,d)||
		   _2(b-c,a,d)||
		   _2(c-b,a,d)||
		   _2(b*c,a,d)||
		   _2(b/c,a,d)||
		   _2(c/b,a,d)||
		   _2(b+d,a,c)||
		   _2(b-d,a,c)||
		   _2(d-b,a,c)||
		   _2(b*d,a,c)||
		   _2(b/d,a,c)||
		   _2(d/b,a,c)||
		   _2(c+d,a,b)||
		   _2(c-d,a,b)||
		   _2(d-c,a,b)||
		   _2(c*d,a,b)||
		   _2(c/d,a,b)||
		   _2(d/c,a,b);
}
bool check24(int a,int b,int c,int d){
	return _1(a,b,c,d)
}
int main(){
	int a,b,c,d;
	scanf("%d%d%d%d",&a,&b,&c,&d);
	while(a&&b&&c&&d){
		printf(check24(a,b,c,d)?"YES":"NO");
		printf("\n");
		scanf("%d%d%d%d",&a,&b,&c,&d);
	}
	return 0;
}
