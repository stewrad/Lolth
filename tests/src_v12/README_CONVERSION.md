Lolth v7: Angular display conversion + legacy pickle ingestion

Plot Phi-Theta ON: Theta=A1 and Phi=E1 (original scan grid).
OFF: Azimuth=wrapTo360(180-Theta), vertical angle=wrapTo360(180-Phi).
These are display flips only; data are not interpolated or regridded.

Legacy nested pickles with outer File/Freq/P/E1/Data rows are expanded during ingestion.
Nested Data may be a frame, dict, or numeric angular array. A1 and E1 are retained.
If saved using newer pandas string extension dtypes, matching pandas versions may be
needed to unpickle successfully.

Run from project root: PYTHONPATH=src python -m Lolth
