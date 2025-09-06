from cubing_algs.vcube import VCube


def show_f2l_oriented(orientation):
    c = VCube()

    c.rotate(f"{ orientation } z2 R U' R' U R' F R F' U".strip())

    print(f'{ orientation} ====>')
    c.show('f2l')


show_f2l_oriented('')
show_f2l_oriented('y')
show_f2l_oriented('y2')
show_f2l_oriented("y'")
