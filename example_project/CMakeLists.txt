cmake_minimum_required( VERSION 3.22 )  
	
project( example_project )

set( sources main.cpp )  	     

add_executable( main ${sources} )

add_subdirectory( dir1 )
add_subdirectory( dir2 )
