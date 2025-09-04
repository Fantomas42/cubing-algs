from cubing_algs.vcube import VCube


def show_cube_oriented(faces):
    cube = VCube()
    cube.rotate("R U R' U'")
    cube.orient(*faces)

    print(faces, '====>')
    cube.show()


show_cube_oriented('UF')
show_cube_oriented('UB')
show_cube_oriented('UR')
show_cube_oriented('UL')

show_cube_oriented('DF')
show_cube_oriented('DB')
show_cube_oriented('DR')
show_cube_oriented('DL')

show_cube_oriented('FU')
show_cube_oriented('FD')
show_cube_oriented('FR')
show_cube_oriented('FL')

show_cube_oriented('BU')
show_cube_oriented('BD')
show_cube_oriented('BR')
show_cube_oriented('BL')

show_cube_oriented('RU')
show_cube_oriented('RD')
show_cube_oriented('RF')
show_cube_oriented('RB')

show_cube_oriented('LU')
show_cube_oriented('LD')
show_cube_oriented('LF')
show_cube_oriented('LB')
