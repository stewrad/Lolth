Legacy nested pickle support
============================
Nested Data cells may be shaped (4, N) or (N, 4). The legacy four fields are
A1 (sweep angle), I, Q, PdBsm. Row-level E1 (cut angle) and Freq are repeated
over the unpacked samples. Internal aliases Theta=A1, Phi=E1, PdB=PdBsm
are provided without removing original fields.

A pickle made with a newer pandas version may require that same or a later
pandas version to deserialize.
