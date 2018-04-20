void sort2(n,ra,rb)
int n;
double *ra,*rb;
{
	int l,j,ir,i;
	double rrb,rra;

	l=(n >> 1)+1;
	ir=n;
	for (;;) {
		if (l > 1) {
			rra=ra[--l];
			rrb=rb[l];
		} else {
			rra=ra[ir];
			rrb=rb[ir];
			ra[ir]=ra[1];
			rb[ir]=rb[1];
			if (--ir == 1) {
				ra[1]=rra;
				rb[1]=rrb;
				return;
			}
		}
		i=l;
		j=l << 1;
		while (j <= ir)	{
			if (j < ir && ra[j] < ra[j+1]) ++j;
			if (rra < ra[j]) {
				ra[i]=ra[j];
				rb[i]=rb[j];
				j += (i=j);
			}
			else j=ir+1;
		}
		ra[i]=rra;
		rb[i]=rrb;
	}
}


