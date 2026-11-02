/* P7 driver: calls sim_telarray's own sim_absorb.c functions.
   argv: grid_file altitude_m
   stdin per line: iwl zem_cm airmass ztel_cm pathlen_cm
   The telescope optical depths are computed exactly as sim_telarray.c:1859-1870 does. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "absorb.h"
int main(int argc, char **argv)
{
   double alt = atof(argv[2]);
   if ( read_trans(argv[1], alt) < 0 ) { fprintf(stderr, "read_trans failed\n"); return 1; }
   int iwl; double zem, am, ztel, plen;
   double h2 = height_for_transmission() * 1e5; /* obs level [cm] */
   while ( scanf("%d %lf %lf %lf %lf", &iwl, &zem, &am, &ztel, &plen) == 5 )
   {
      double t1 = atmospheric_transmission(iwl, h2 + ztel, 1.0);        /* sim_telarray.c:1859 */
      double t2 = atmospheric_transmission(iwl, h2 + ztel + plen, 1.0); /* sim_telarray.c:1860 */
      double od_tel, od_focus;
      if ( t1 <= 0. ) od_tel = 99999.; else od_tel = -log(t1);          /* sim_telarray.c:1862-1864 */
      if ( t1 <= 0. || t2 <= 0. ) od_focus = 99999.;                    /* sim_telarray.c:1866 */
      else od_focus = -log(t2/t1);                                      /* sim_telarray.c:1868 */
      printf("%.17g\n", atmospheric_transmission2(iwl, zem, am, od_tel, od_focus)); /* sim_telarray.c:2861 */
   }
   return 0;
}
