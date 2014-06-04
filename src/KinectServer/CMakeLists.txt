cmake_minimum_required(VERSION 2.8)

# chceme linkovat khinovnu websocketpp

# Boost - hledani knihoven
# -----------------
find_package(Boost COMPONENTS system filesystem date_time program_options thread regex REQUIRED)
find_package(Threads REQUIRED)

# Hledani JSONu
# --------------

# Include adresare - hledani headeru.
# ----------------------------------
file(GLOB ${OPENNI_LIB_NAME}_sources ./*.cpp ./*.h ../../Include/*.h)
include_directories (/usr/local/include/websocketpp)
include_directories(/usr/include/ni)

# Set Link libraries.
# -------------------
# kde se budou hledat zkompilovane khihovny (kvuli boost knihovne, natvrdo nastaveno na cestu tak, jak to ma boost balicek debianu)
LINK_DIRECTORIES(/usr/local/lib)

# Linkovani knihoven.
# ------------------
link_libraries(websocketpp)

# vytvoreni nasi binarky
add_executable (kinect_server kinect_server.cpp)

# linkovani dalsich khihoven, vlaken
target_link_libraries(kinect_server ${OpenCV_LIBS} ${Boost_LIBRARIES} OpenNI)
target_link_libraries(kinect_server ${CMAKE_THREAD_LIBS_INIT})
