cat <<EOF > ${infile}

#== Geometry ==
prompt 0
nx 24
ny 24
nz 24
nt 64
node_geometry 1 1 1 1
ionode_geometry 1 1 1 1
iseed 9941
job_id debug

#== Gauge ==
reload_serial /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/lat/v5/l2464f211b600m0102m0509m635a.${cfg}
u0 0.835
no_gauge_fix
forget
staple_weight 0.05
ape_iter 20
coordinate_origin 0 0 0 0
time_bc antiperiodic

#== PBP Masses ==

number_of_pbp_masses 0

#== Base Sources ==

number_of_base_sources 2

#== source 0: RandomColorWallSource ==
random_color_wall
subset corner
t0 41
ncolor 1
momentum 0 0 0
source_label RW
save_partfile_scidac_ks_source /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/rand/rnd_2464f211b600m0102m0509m635_t0.a${cfg}

#== source 1: VectorFieldSource ==
vector_field
subset corner
origin 0 0 0 0
load_source_serial /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/rand/rnd_2464f211b600m0102m0509m635_t0.a${cfg}
ncolor 1
momentum 0 0 0
source_label RW
forget_source

#== Modified Sources ==

number_of_modified_sources 0

#== KSsolveSets ==

number_of_sets 5

#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check sourceonly
momentum_twist 0 0 0
precision 1
source 0
number_of_propagators 1

#== propagator 0: KSsolveElement ==
mass 1.0
naik_term_epsilon 0.
error_for_propagator 1
rel_error_for_propagator 0.0
fresh_ksprop
forget_ksprop

EOF

errLs=[ 1e-3 1e-5 1e-7 1e-9 ]
errRs=[ 1e-3 1e-5 1e-7 ]

for ((k=0; k<4; k++)); do
err=$errs[$k]
cat <<EOF >> ${infile}

#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 1
number_of_propagators 4

#== propagator 1: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator ${err}
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.0,0,0+d_2464f211b600m0102m0509m635_t0.${err}.a${cfg}

#== propagator 2: KSsolveElement ==
mass 0.053476
naik_term_epsilon 0.
error_for_propagator ${err}
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qstrange+0.053476+0.+q+d.0,0,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== propagator 3: KSsolveElement ==
mass 0.6363
naik_term_epsilon -0.229787
error_for_propagator 0.0
rel_error_for_propagator 1e-8
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qheavy+0.6363+-0.229787+q+d.0,0,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== propagator 4: KSsolveElement ==
mass 1.2726
naik_term_epsilon -0.521
error_for_propagator 0.0
rel_error_for_propagator 1e-8
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qheavy+1.2726+-0.521+q+d.0,0,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 2
number_of_propagators 2

#== propagator 5: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.1,0,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== propagator 6: KSsolveElement ==
mass 0.053476
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qstrange+0.053476+0.+q+d.1,0,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 3
number_of_propagators 2

#== propagator 7: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.1,1,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== propagator 8: KSsolveElement ==
mass 0.053476
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qstrange+0.053476+0.+q+d.1,1,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 4
number_of_propagators 2

#== propagator 9: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.2,0,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== propagator 10: KSsolveElement ==
mass 0.053476
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qstrange+0.053476+0.+q+d.2,0,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 5
number_of_propagators 2

#== propagator 11: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.2,1,1+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== propagator 12: KSsolveElement ==
mass 0.053476
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qstrange+0.053476+0.+q+d.2,1,1+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 6
number_of_propagators 2

#== propagator 13: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.3,0,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== propagator 14: KSsolveElement ==
mass 0.053476
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/allHISQ/l2464f211b600m0102m0509m635/prop/prop_loose+qstrange+0.053476+0.+q+d.3,0,0+d_2464f211b600m0102m0509m635_t0.a${cfg}


#== Quarks ==

number_of_quarks 14

#== quark 0: QuarkIdentitySink ==
propagator 1
identity
op_label d
forget_ksprop

#== quark 1: QuarkIdentitySink ==
propagator 2
identity
op_label d
forget_ksprop

#== quark 2: QuarkIdentitySink ==
propagator 3
identity
op_label d
forget_ksprop

#== quark 3: QuarkIdentitySink ==
propagator 4
identity
op_label d
forget_ksprop

#== quark 4: QuarkIdentitySink ==
propagator 5
identity
op_label d
forget_ksprop

#== quark 5: QuarkIdentitySink ==
propagator 6
identity
op_label d
forget_ksprop

#== quark 6: QuarkIdentitySink ==
propagator 7
identity
op_label d
forget_ksprop

#== quark 7: QuarkIdentitySink ==
propagator 8
identity
op_label d
forget_ksprop

#== quark 8: QuarkIdentitySink ==
propagator 9
identity
op_label d
forget_ksprop

#== quark 9: QuarkIdentitySink ==
propagator 10
identity
op_label d
forget_ksprop

#== quark 10: QuarkIdentitySink ==
propagator 11
identity
op_label d
forget_ksprop

#== quark 11: QuarkIdentitySink ==
propagator 12
identity
op_label d
forget_ksprop

#== quark 12: QuarkIdentitySink ==
propagator 13
identity
op_label d
forget_ksprop

#== quark 13: QuarkIdentitySink ==
propagator 14
identity
op_label d
forget_ksprop

#== Mesons ==

number_of_mesons 36

#== MesonSpectrum ==
pair 2 10
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m0.6363-p211/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p211 1 / 576.0 G5-G5 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 2 6
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m0.6363-p110/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p110 1 / 576.0 G5-G5 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 2 4
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m0.6363-p100/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p100 1 / 576.0 G5-G5 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m0.6363-p000/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p000 1 / 576.0 G5-G5 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 12
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m0.6363-p300/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p300 1 / 576.0 G5-G5 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 8
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m0.6363-p200/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p200 1 / 576.0 G5-G5 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 10
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m1.2726-p211/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p211 1 / 576.0 G5-G5 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 3 6
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m1.2726-p110/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p110 1 / 576.0 G5-G5 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 3 4
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m1.2726-p100/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p100 1 / 576.0 G5-G5 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m1.2726-p000/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p000 1 / 576.0 G5-G5 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 12
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m1.2726-p300/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p300 1 / 576.0 G5-G5 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 8
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/H/m0.0102-m1.2726-p200/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p200 1 / 576.0 G5-G5 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 1 10
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/K/m0.0102-m0.053476-p211/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p211 1 / 576.0 G5-G5 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 1 6
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/K/m0.0102-m0.053476-p110/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p110 1 / 576.0 G5-G5 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 1 4
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/K/m0.0102-m0.053476-p100/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p100 1 / 576.0 G5-G5 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 1 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/K/m0.0102-m0.053476-p000/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p000 1 / 576.0 G5-G5 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 1 12
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/K/m0.0102-m0.053476-p300/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p300 1 / 576.0 G5-G5 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 1 8
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/K/m0.0102-m0.053476-p200/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p200 1 / 576.0 G5-G5 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 0 10
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/pi/m0.0102-m0.0102-p211/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p211 1 / 576.0 G5-G5 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 0 6
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/pi/m0.0102-m0.0102-p110/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p110 1 / 576.0 G5-G5 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 0 4
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/pi/m0.0102-m0.0102-p100/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p100 1 / 576.0 G5-G5 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 0 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/pi/m0.0102-m0.0102-p000/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p000 1 / 576.0 G5-G5 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 0 12
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/pi/m0.0102-m0.0102-p300/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p300 1 / 576.0 G5-G5 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 0 8
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/pi/m0.0102-m0.0102-p200/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p200 1 / 576.0 G5-G5 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 11
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m0.6363-p211/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p211 1 / 576.0 G5-G5 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 2 7
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m0.6363-p110/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p110 1 / 576.0 G5-G5 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 2 5
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m0.6363-p100/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p100 1 / 576.0 G5-G5 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 1
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m0.6363-p000/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p000 1 / 576.0 G5-G5 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 13
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m0.6363-p300/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p300 1 / 576.0 G5-G5 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 9
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m0.6363-p200/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p200 1 / 576.0 G5-G5 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 11
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m1.2726-p211/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p211 1 / 576.0 G5-G5 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 3 7
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m1.2726-p110/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p110 1 / 576.0 G5-G5 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 3 5
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m1.2726-p100/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p100 1 / 576.0 G5-G5 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 1
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m1.2726-p000/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p000 1 / 576.0 G5-G5 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 13
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m1.2726-p300/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p300 1 / 576.0 G5-G5 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 9
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/Hs/m0.053476-m1.2726-p200/corr2pt_a${cfg}
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5 p200 1 / 576.0 G5-G5 -2 0 0 EO EO EO

#== Baryons ==

number_of_baryons 0

EOF


#== Geometry ==
prompt 0
nx 24
ny 24
nz 24
nt 64
node_geometry 2 2 3 4
ionode_geometry 1 1 1 4 
iseed 9941
job_id debug

#== Gauge ==
reload_serial /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/lat/v5/l2464f211b600m0102m0509m635x.99
u0 0.835
no_gauge_fix
f o r g e t
staple_weight 0.05
ape_iter 20
coordinate_origin 0 0 0 41
time_bc antiperiodic

#== PBP Masses ==

number_of_pbp_masses 0

#== Base Sources ==

number_of_base_sources 7

#== source 0: RandomColorWallSource ==
random_color_wall
subset corner
t0 41
ncolor 1
momentum 0 0 0
source_label RW
save_partfile_scidac_ks_source /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/rand/rnd_2464f211b600m0102m0509m635_t41.x000099

#== source 1: VectorFieldSource ==
vector_field
subset corner
origin 0 0 0 41
load_source_serial /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/rand/rnd_2464f211b600m0102m0509m635_t41.x000099
ncolor 1
momentum 0 0 0
source_label RW
forget_source

#== source 2: VectorFieldSource ==
vector_field
subset corner
origin 0 0 0 41
load_source_serial /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/rand/rnd_2464f211b600m0102m0509m635_t41.x000099
ncolor 1
momentum 1 0 0
source_label RW
forget_source

#== source 3: VectorFieldSource ==
vector_field
subset corner
origin 0 0 0 41
load_source_serial /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/rand/rnd_2464f211b600m0102m0509m635_t41.x000099
ncolor 1
momentum 1 1 0
source_label RW
forget_source

#== source 4: VectorFieldSource ==
vector_field
subset corner
origin 0 0 0 41
load_source_serial /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/rand/rnd_2464f211b600m0102m0509m635_t41.x000099
ncolor 1
momentum 2 0 0
source_label RW
forget_source

#== source 5: VectorFieldSource ==
vector_field
subset corner
origin 0 0 0 41
load_source_serial /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/rand/rnd_2464f211b600m0102m0509m635_t41.x000099
ncolor 1
momentum 2 1 1
source_label RW
forget_source

#== source 6: VectorFieldSource ==
vector_field
subset corner
origin 0 0 0 41
load_source_serial /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/rand/rnd_2464f211b600m0102m0509m635_t41.x000099
ncolor 1
momentum 3 0 0
source_label RW
forget_source

#== Modified Sources ==

number_of_modified_sources 0

#== KSsolveSets ==

number_of_sets 7

#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check sourceonly
momentum_twist 0 0 0
precision 1
source 0
number_of_propagators 1

#== propagator 0: KSsolveElement ==
mass 1.0
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
forget_ksprop


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 1
number_of_propagators 1

#== propagator 1: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.0,0,0+d_2464f211b600m0102m0509m635_t41.x000099


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 2
number_of_propagators 1

#== propagator 2: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.1,0,0+d_2464f211b600m0102m0509m635_t41.x000099


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 3
number_of_propagators 1

#== propagator 3: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.1,1,0+d_2464f211b600m0102m0509m635_t41.x000099


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 4
number_of_propagators 1

#== propagator 4: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.2,0,0+d_2464f211b600m0102m0509m635_t41.x000099


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 5
number_of_propagators 1

#== propagator 5: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.2,1,1+d_2464f211b600m0102m0509m635_t41.x000099


#== KSsolveSet ==
max_cg_iterations 4000
max_cg_restarts 5
check yes
momentum_twist 0 0 0
precision 2
source 6
number_of_propagators 1

#== propagator 6: KSsolveElement ==
mass 0.0102
naik_term_epsilon 0.
error_for_propagator 1e-5
rel_error_for_propagator 0.0
fresh_ksprop
save_partfile_scidac_ksprop /lqcdproj/fermimilcheavylight/detar/Bpilnu/l2464f211b600m0102m0509m635/prop/prop_loose+qlight+0.0102+0.+q+d.3,0,0+d_2464f211b600m0102m0509m635_t41.x000099


#== Quarks ==

number_of_quarks 30

#== quark 0: QuarkIdentitySink ==
propagator 1
identity
op_label d
forget_ksprop

#== quark 1: KSExtSrcSink ==
quark 0
ext_src_ks
spin_taste_extend G5T-G5T
momentum 0 0 0
t0 56
op_label x
forget_ksprop

#== quark 2: KSInverseSink ==
quark 1
ks_inverse
mass 0.6363
naik_term_epsilon -0.229787
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 3: KSInverseSink ==
quark 1
ks_inverse
mass 1.2726
naik_term_epsilon -0.521
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 4: KSExtSrcSink ==
quark 0
ext_src_ks
spin_taste_extend G5T-G5T
momentum 0 0 0
t0 59
op_label x
forget_ksprop

#== quark 5: KSInverseSink ==
quark 4
ks_inverse
mass 0.6363
naik_term_epsilon -0.229787
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 6: KSInverseSink ==
quark 4
ks_inverse
mass 1.2726
naik_term_epsilon -0.521
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 7: KSExtSrcSink ==
quark 0
ext_src_ks
spin_taste_extend G5T-G5T
momentum 0 0 0
t0 61
op_label x
forget_ksprop

#== quark 8: KSInverseSink ==
quark 7
ks_inverse
mass 0.6363
naik_term_epsilon -0.229787
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 9: KSInverseSink ==
quark 7
ks_inverse
mass 1.2726
naik_term_epsilon -0.521
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 10: KSExtSrcSink ==
quark 0
ext_src_ks
spin_taste_extend G5T-G5T
momentum 0 0 0
t0 62
op_label x
forget_ksprop

#== quark 11: KSInverseSink ==
quark 10
ks_inverse
mass 0.6363
naik_term_epsilon -0.229787
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 12: KSInverseSink ==
quark 10
ks_inverse
mass 1.2726
naik_term_epsilon -0.521
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 13: KSExtSrcSink ==
quark 0
ext_src_ks
spin_taste_extend G5-G5
momentum 0 0 0
t0 56
op_label x
forget_ksprop

#== quark 14: KSInverseSink ==
quark 13
ks_inverse
mass 0.6363
naik_term_epsilon -0.229787
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 15: KSInverseSink ==
quark 13
ks_inverse
mass 1.2726
naik_term_epsilon -0.521
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 16: KSExtSrcSink ==
quark 0
ext_src_ks
spin_taste_extend G5-G5
momentum 0 0 0
t0 59
op_label x
forget_ksprop

#== quark 17: KSInverseSink ==
quark 16
ks_inverse
mass 0.6363
naik_term_epsilon -0.229787
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 18: KSInverseSink ==
quark 16
ks_inverse
mass 1.2726
naik_term_epsilon -0.521
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 19: KSExtSrcSink ==
quark 0
ext_src_ks
spin_taste_extend G5-G5
momentum 0 0 0
t0 61
op_label x
forget_ksprop

#== quark 20: KSInverseSink ==
quark 19
ks_inverse
mass 0.6363
naik_term_epsilon -0.229787
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 21: KSInverseSink ==
quark 19
ks_inverse
mass 1.2726
naik_term_epsilon -0.521
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 22: KSExtSrcSink ==
quark 0
ext_src_ks
spin_taste_extend G5-G5
momentum 0 0 0
t0 62
op_label x
forget_ksprop

#== quark 23: KSInverseSink ==
quark 22
ks_inverse
mass 0.6363
naik_term_epsilon -0.229787
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 24: KSInverseSink ==
quark 22
ks_inverse
mass 1.2726
naik_term_epsilon -0.521
u0 0.835
max_cg_iterations 400
max_cg_restarts 5
error_for_propagator 0.0
rel_error_for_propagator 1e-8
precision 2
momentum_twist 0 0 0
op_label x
forget_ksprop

#== quark 25: QuarkIdentitySink ==
propagator 2
identity
op_label d
forget_ksprop

#== quark 26: QuarkIdentitySink ==
propagator 3
identity
op_label d
forget_ksprop

#== quark 27: QuarkIdentitySink ==
propagator 4
identity
op_label d
forget_ksprop

#== quark 28: QuarkIdentitySink ==
propagator 5
identity
op_label d
forget_ksprop

#== quark 29: QuarkIdentitySink ==
propagator 6
identity
op_label d
forget_ksprop

#== Mesons ==

number_of_mesons 96

#== MesonSpectrum ==
pair 2 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p211/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 4
correlator A4-A4_V4-V4_T15_m0.6363 p211 -1 / 576.0 GT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T14-V4_T15_m0.6363 p211 1 / 576.0 GXT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T24-V4_T15_m0.6363 p211 -1 / 576.0 GYT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T34-V4_T15_m0.6363 p211 1 / 576.0 GZT-GT -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 2 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p110/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 3
correlator A4-A4_V4-V4_T15_m0.6363 p110 -1 / 576.0 GT-GT -1 -1 0 EO EO EO
correlator A4-A4_T14-V4_T15_m0.6363 p110 1 / 576.0 GXT-GT -1 -1 0 EO EO EO
correlator A4-A4_T24-V4_T15_m0.6363 p110 -1 / 576.0 GYT-GT -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 2 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p100/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T15_m0.6363 p100 -1 / 576.0 GT-GT -1 0 0 EO EO EO
correlator A4-A4_T14-V4_T15_m0.6363 p100 1 / 576.0 GXT-GT -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p000/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator A4-A4_V4-V4_T15_m0.6363 p000 -1 / 576.0 GT-GT 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p300/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T15_m0.6363 p300 -1 / 576.0 GT-GT -3 0 0 EO EO EO
correlator A4-A4_T14-V4_T15_m0.6363 p300 1 / 576.0 GXT-GT -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 2 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p200/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T15_m0.6363 p200 -1 / 576.0 GT-GT -2 0 0 EO EO EO
correlator A4-A4_T14-V4_T15_m0.6363 p200 1 / 576.0 GXT-GT -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p211/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 4
correlator A4-A4_V4-V4_T15_m1.2726 p211 -1 / 576.0 GT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T14-V4_T15_m1.2726 p211 1 / 576.0 GXT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T24-V4_T15_m1.2726 p211 -1 / 576.0 GYT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T34-V4_T15_m1.2726 p211 1 / 576.0 GZT-GT -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 3 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p110/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 3
correlator A4-A4_V4-V4_T15_m1.2726 p110 -1 / 576.0 GT-GT -1 -1 0 EO EO EO
correlator A4-A4_T14-V4_T15_m1.2726 p110 1 / 576.0 GXT-GT -1 -1 0 EO EO EO
correlator A4-A4_T24-V4_T15_m1.2726 p110 -1 / 576.0 GYT-GT -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 3 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p100/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T15_m1.2726 p100 -1 / 576.0 GT-GT -1 0 0 EO EO EO
correlator A4-A4_T14-V4_T15_m1.2726 p100 1 / 576.0 GXT-GT -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p000/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator A4-A4_V4-V4_T15_m1.2726 p000 -1 / 576.0 GT-GT 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p300/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T15_m1.2726 p300 -1 / 576.0 GT-GT -3 0 0 EO EO EO
correlator A4-A4_T14-V4_T15_m1.2726 p300 1 / 576.0 GXT-GT -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 3 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p200/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T15_m1.2726 p200 -1 / 576.0 GT-GT -2 0 0 EO EO EO
correlator A4-A4_T14-V4_T15_m1.2726 p200 1 / 576.0 GXT-GT -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 5 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p211/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 4
correlator A4-A4_V4-V4_T18_m0.6363 p211 -1 / 576.0 GT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T14-V4_T18_m0.6363 p211 1 / 576.0 GXT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T24-V4_T18_m0.6363 p211 -1 / 576.0 GYT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T34-V4_T18_m0.6363 p211 1 / 576.0 GZT-GT -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 5 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p110/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 3
correlator A4-A4_V4-V4_T18_m0.6363 p110 -1 / 576.0 GT-GT -1 -1 0 EO EO EO
correlator A4-A4_T14-V4_T18_m0.6363 p110 1 / 576.0 GXT-GT -1 -1 0 EO EO EO
correlator A4-A4_T24-V4_T18_m0.6363 p110 -1 / 576.0 GYT-GT -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 5 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p100/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T18_m0.6363 p100 -1 / 576.0 GT-GT -1 0 0 EO EO EO
correlator A4-A4_T14-V4_T18_m0.6363 p100 1 / 576.0 GXT-GT -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 5 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p000/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator A4-A4_V4-V4_T18_m0.6363 p000 -1 / 576.0 GT-GT 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 5 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p300/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T18_m0.6363 p300 -1 / 576.0 GT-GT -3 0 0 EO EO EO
correlator A4-A4_T14-V4_T18_m0.6363 p300 1 / 576.0 GXT-GT -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 5 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p200/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T18_m0.6363 p200 -1 / 576.0 GT-GT -2 0 0 EO EO EO
correlator A4-A4_T14-V4_T18_m0.6363 p200 1 / 576.0 GXT-GT -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 6 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p211/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 4
correlator A4-A4_V4-V4_T18_m1.2726 p211 -1 / 576.0 GT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T14-V4_T18_m1.2726 p211 1 / 576.0 GXT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T24-V4_T18_m1.2726 p211 -1 / 576.0 GYT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T34-V4_T18_m1.2726 p211 1 / 576.0 GZT-GT -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 6 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p110/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 3
correlator A4-A4_V4-V4_T18_m1.2726 p110 -1 / 576.0 GT-GT -1 -1 0 EO EO EO
correlator A4-A4_T14-V4_T18_m1.2726 p110 1 / 576.0 GXT-GT -1 -1 0 EO EO EO
correlator A4-A4_T24-V4_T18_m1.2726 p110 -1 / 576.0 GYT-GT -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 6 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p100/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T18_m1.2726 p100 -1 / 576.0 GT-GT -1 0 0 EO EO EO
correlator A4-A4_T14-V4_T18_m1.2726 p100 1 / 576.0 GXT-GT -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 6 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p000/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator A4-A4_V4-V4_T18_m1.2726 p000 -1 / 576.0 GT-GT 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 6 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p300/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T18_m1.2726 p300 -1 / 576.0 GT-GT -3 0 0 EO EO EO
correlator A4-A4_T14-V4_T18_m1.2726 p300 1 / 576.0 GXT-GT -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 6 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p200/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T18_m1.2726 p200 -1 / 576.0 GT-GT -2 0 0 EO EO EO
correlator A4-A4_T14-V4_T18_m1.2726 p200 1 / 576.0 GXT-GT -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 8 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p211/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 4
correlator A4-A4_V4-V4_T20_m0.6363 p211 -1 / 576.0 GT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T14-V4_T20_m0.6363 p211 1 / 576.0 GXT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T24-V4_T20_m0.6363 p211 -1 / 576.0 GYT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T34-V4_T20_m0.6363 p211 1 / 576.0 GZT-GT -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 8 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p110/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 3
correlator A4-A4_V4-V4_T20_m0.6363 p110 -1 / 576.0 GT-GT -1 -1 0 EO EO EO
correlator A4-A4_T14-V4_T20_m0.6363 p110 1 / 576.0 GXT-GT -1 -1 0 EO EO EO
correlator A4-A4_T24-V4_T20_m0.6363 p110 -1 / 576.0 GYT-GT -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 8 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p100/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T20_m0.6363 p100 -1 / 576.0 GT-GT -1 0 0 EO EO EO
correlator A4-A4_T14-V4_T20_m0.6363 p100 1 / 576.0 GXT-GT -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 8 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p000/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator A4-A4_V4-V4_T20_m0.6363 p000 -1 / 576.0 GT-GT 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 8 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p300/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T20_m0.6363 p300 -1 / 576.0 GT-GT -3 0 0 EO EO EO
correlator A4-A4_T14-V4_T20_m0.6363 p300 1 / 576.0 GXT-GT -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 8 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p200/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T20_m0.6363 p200 -1 / 576.0 GT-GT -2 0 0 EO EO EO
correlator A4-A4_T14-V4_T20_m0.6363 p200 1 / 576.0 GXT-GT -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 9 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p211/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 4
correlator A4-A4_V4-V4_T20_m1.2726 p211 -1 / 576.0 GT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T14-V4_T20_m1.2726 p211 1 / 576.0 GXT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T24-V4_T20_m1.2726 p211 -1 / 576.0 GYT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T34-V4_T20_m1.2726 p211 1 / 576.0 GZT-GT -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 9 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p110/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 3
correlator A4-A4_V4-V4_T20_m1.2726 p110 -1 / 576.0 GT-GT -1 -1 0 EO EO EO
correlator A4-A4_T14-V4_T20_m1.2726 p110 1 / 576.0 GXT-GT -1 -1 0 EO EO EO
correlator A4-A4_T24-V4_T20_m1.2726 p110 -1 / 576.0 GYT-GT -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 9 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p100/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T20_m1.2726 p100 -1 / 576.0 GT-GT -1 0 0 EO EO EO
correlator A4-A4_T14-V4_T20_m1.2726 p100 1 / 576.0 GXT-GT -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 9 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p000/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator A4-A4_V4-V4_T20_m1.2726 p000 -1 / 576.0 GT-GT 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 9 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p300/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T20_m1.2726 p300 -1 / 576.0 GT-GT -3 0 0 EO EO EO
correlator A4-A4_T14-V4_T20_m1.2726 p300 1 / 576.0 GXT-GT -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 9 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p200/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T20_m1.2726 p200 -1 / 576.0 GT-GT -2 0 0 EO EO EO
correlator A4-A4_T14-V4_T20_m1.2726 p200 1 / 576.0 GXT-GT -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 11 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p211/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 4
correlator A4-A4_V4-V4_T21_m0.6363 p211 -1 / 576.0 GT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T14-V4_T21_m0.6363 p211 1 / 576.0 GXT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T24-V4_T21_m0.6363 p211 -1 / 576.0 GYT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T34-V4_T21_m0.6363 p211 1 / 576.0 GZT-GT -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 11 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p110/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 3
correlator A4-A4_V4-V4_T21_m0.6363 p110 -1 / 576.0 GT-GT -1 -1 0 EO EO EO
correlator A4-A4_T14-V4_T21_m0.6363 p110 1 / 576.0 GXT-GT -1 -1 0 EO EO EO
correlator A4-A4_T24-V4_T21_m0.6363 p110 -1 / 576.0 GYT-GT -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 11 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p100/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T21_m0.6363 p100 -1 / 576.0 GT-GT -1 0 0 EO EO EO
correlator A4-A4_T14-V4_T21_m0.6363 p100 1 / 576.0 GXT-GT -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 11 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p000/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator A4-A4_V4-V4_T21_m0.6363 p000 -1 / 576.0 GT-GT 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 11 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p300/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T21_m0.6363 p300 -1 / 576.0 GT-GT -3 0 0 EO EO EO
correlator A4-A4_T14-V4_T21_m0.6363 p300 1 / 576.0 GXT-GT -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 11 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m0.6363-m0.0102-p200/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T21_m0.6363 p200 -1 / 576.0 GT-GT -2 0 0 EO EO EO
correlator A4-A4_T14-V4_T21_m0.6363 p200 1 / 576.0 GXT-GT -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 12 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p211/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 4
correlator A4-A4_V4-V4_T21_m1.2726 p211 -1 / 576.0 GT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T14-V4_T21_m1.2726 p211 1 / 576.0 GXT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T24-V4_T21_m1.2726 p211 -1 / 576.0 GYT-GT -2 -1 -1 EO EO EO
correlator A4-A4_T34-V4_T21_m1.2726 p211 1 / 576.0 GZT-GT -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 12 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p110/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 3
correlator A4-A4_V4-V4_T21_m1.2726 p110 -1 / 576.0 GT-GT -1 -1 0 EO EO EO
correlator A4-A4_T14-V4_T21_m1.2726 p110 1 / 576.0 GXT-GT -1 -1 0 EO EO EO
correlator A4-A4_T24-V4_T21_m1.2726 p110 -1 / 576.0 GYT-GT -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 12 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p100/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T21_m1.2726 p100 -1 / 576.0 GT-GT -1 0 0 EO EO EO
correlator A4-A4_T14-V4_T21_m1.2726 p100 1 / 576.0 GXT-GT -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 12 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p000/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator A4-A4_V4-V4_T21_m1.2726 p000 -1 / 576.0 GT-GT 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 12 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p300/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T21_m1.2726 p300 -1 / 576.0 GT-GT -3 0 0 EO EO EO
correlator A4-A4_T14-V4_T21_m1.2726 p300 1 / 576.0 GXT-GT -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 12 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HV2pi/m0.0102-m1.2726-m0.0102-p200/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 2
correlator A4-A4_V4-V4_T21_m1.2726 p200 -1 / 576.0 GT-GT -2 0 0 EO EO EO
correlator A4-A4_T14-V4_T21_m1.2726 p200 1 / 576.0 GXT-GT -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 14 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p211/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m0.6363 p211 1 / 576.0 G1-G1 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 14 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p110/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m0.6363 p110 1 / 576.0 G1-G1 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 14 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p100/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m0.6363 p100 1 / 576.0 G1-G1 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 14 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p000/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m0.6363 p000 1 / 576.0 G1-G1 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 14 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p300/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m0.6363 p300 1 / 576.0 G1-G1 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 14 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p200/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m0.6363 p200 1 / 576.0 G1-G1 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 15 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p211/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m1.2726 p211 1 / 576.0 G1-G1 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 15 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p110/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m1.2726 p110 1 / 576.0 G1-G1 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 15 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p100/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m1.2726 p100 1 / 576.0 G1-G1 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 15 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p000/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m1.2726 p000 1 / 576.0 G1-G1 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 15 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p300/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m1.2726 p300 1 / 576.0 G1-G1 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 15 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p200/corr3pt_T15_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T15_m1.2726 p200 1 / 576.0 G1-G1 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 17 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p211/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m0.6363 p211 1 / 576.0 G1-G1 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 17 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p110/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m0.6363 p110 1 / 576.0 G1-G1 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 17 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p100/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m0.6363 p100 1 / 576.0 G1-G1 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 17 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p000/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m0.6363 p000 1 / 576.0 G1-G1 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 17 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p300/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m0.6363 p300 1 / 576.0 G1-G1 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 17 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p200/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m0.6363 p200 1 / 576.0 G1-G1 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 18 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p211/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m1.2726 p211 1 / 576.0 G1-G1 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 18 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p110/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m1.2726 p110 1 / 576.0 G1-G1 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 18 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p100/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m1.2726 p100 1 / 576.0 G1-G1 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 18 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p000/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m1.2726 p000 1 / 576.0 G1-G1 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 18 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p300/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m1.2726 p300 1 / 576.0 G1-G1 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 18 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p200/corr3pt_T18_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T18_m1.2726 p200 1 / 576.0 G1-G1 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 20 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p211/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m0.6363 p211 1 / 576.0 G1-G1 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 20 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p110/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m0.6363 p110 1 / 576.0 G1-G1 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 20 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p100/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m0.6363 p100 1 / 576.0 G1-G1 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 20 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p000/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m0.6363 p000 1 / 576.0 G1-G1 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 20 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p300/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m0.6363 p300 1 / 576.0 G1-G1 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 20 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p200/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m0.6363 p200 1 / 576.0 G1-G1 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 21 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p211/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m1.2726 p211 1 / 576.0 G1-G1 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 21 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p110/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m1.2726 p110 1 / 576.0 G1-G1 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 21 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p100/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m1.2726 p100 1 / 576.0 G1-G1 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 21 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p000/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m1.2726 p000 1 / 576.0 G1-G1 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 21 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p300/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m1.2726 p300 1 / 576.0 G1-G1 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 21 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p200/corr3pt_T20_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T20_m1.2726 p200 1 / 576.0 G1-G1 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 23 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p211/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m0.6363 p211 1 / 576.0 G1-G1 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 23 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p110/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m0.6363 p110 1 / 576.0 G1-G1 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 23 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p100/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m0.6363 p100 1 / 576.0 G1-G1 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 23 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p000/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m0.6363 p000 1 / 576.0 G1-G1 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 23 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p300/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m0.6363 p300 1 / 576.0 G1-G1 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 23 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m0.6363-m0.0102-p200/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m0.6363 p200 1 / 576.0 G1-G1 -2 0 0 EO EO EO

#== MesonSpectrum ==
pair 24 28
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p211/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m1.2726 p211 1 / 576.0 G1-G1 -2 -1 -1 EO EO EO

#== MesonSpectrum ==
pair 24 26
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p110/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m1.2726 p110 1 / 576.0 G1-G1 -1 -1 0 EO EO EO

#== MesonSpectrum ==
pair 24 25
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p100/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m1.2726 p100 1 / 576.0 G1-G1 -1 0 0 EO EO EO

#== MesonSpectrum ==
pair 24 0
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p000/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m1.2726 p000 1 / 576.0 G1-G1 0 0 0 EO EO EO

#== MesonSpectrum ==
pair 24 29
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p300/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m1.2726 p300 1 / 576.0 G1-G1 -3 0 0 EO EO EO

#== MesonSpectrum ==
pair 24 27
spectrum_request meson
save_corr_fnal /project/heavylight/hisq/allHISQ/a0.12/l2464f211b600m0102m0509m635/run1/data/loose/HS2pi/m0.0102-m1.2726-m0.0102-p200/corr3pt_T21_x000099
r_offset 0 0 0 41
number_of_correlators 1
correlator P5-P5_S-S_T21_m1.2726 p200 1 / 576.0 G1-G1 -2 0 0 EO EO EO

#== Baryons ==

number_of_baryons 0
