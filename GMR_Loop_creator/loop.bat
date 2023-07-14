@echo off
echo .......................................
echo Python v3.9, SMR loop calculator v0.2.0
echo .......................................
REM "C:/W10DEV/Anaconda3/envs/geo_py36/python.exe" "%cd%\GMR_loop_creator_v3\loop_calculator.py" "-f" "%cd%"
"C:/W10DEV/Anaconda3/envs/geo_py36/python.exe" "%cd%\create_loop.py" "-f" "%cd%"
pause