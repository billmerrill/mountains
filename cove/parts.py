
def make_pt(x,y,z=None):
    if z is None:
        z = float(emap[y][x]) * pt_scalar[PZ]
    else:
        z = z * pt_scalar[PX]

    return (float(x) * pt_scalar[PX],
            float(y) * pt_scalar[PY],
            z)


def build_mesh_floor(mesh):
    tris = []
    
    # yhalf = sample_height / 2
    yhalf = mesh.get_data_y_size() / 2
    # xhalf = sample_width / 2
    xhalf = mesh.get_data_x_size() / 2
    yquarter = mesh.get_data_y_size() / 2
    xquarter = mesh.get_data_x_size() / 2
    # yquarter = sample_height / 4
    # xquarter = sample_width / 4

    negx = make_pt(xquarter, yhalf, 0)
    posx = make_pt(xquarter + xhalf, yhalf, 0)
    negy = make_pt(xhalf, yquarter, 0)
    posy = make_pt(xhalf, yquarter + yhalf, 0)

    # star inset base
    for sy in range(0, sample_height-1):
        a_triangle = { TA: make_pt(0, sy, 0),
                       TB: negx,
                       TC: make_pt(0, sy+1, 0)}
        z_triangle = { TA: make_pt(sample_width-1, sy, 0),
                      TB: make_pt(sample_width-1, sy+1, 0),
                      TC: posx }

        mesh.append((compute_normal(a_triangle), a_triangle))
        mesh.append((compute_normal(z_triangle), z_triangle))

    for sx in range(0, sample_width-1):
        a_triangle = { TA: make_pt(sx, 0, 0),
                       TB: make_pt(sx+1, 0, 0),
                       TC: negy }
        z_triangle = { TA: make_pt(sx, sample_height-1, 0),
                       TB: posy,
                       TC: make_pt(sx+1, sample_height-1, 0) }

        mesh.append((compute_normal(a_triangle), a_triangle))
        mesh.append((compute_normal(z_triangle), z_triangle))


    a_triangle = { TA: make_pt(0,0,0),
                   TB: negy,
                   TC: negx }
    b_triangle = { TA: negy,
                   TB: make_pt(sample_width-1, 0, 0),
                   TC: posx }
    c_triangle = { TA: posx,
                   TB: make_pt(sample_width-1, sample_height-1, 0),
                   TC: posy }
    d_triangle = { TA: negx,
                   TB: posy,
                   TC: make_pt(0, sample_height-1, 0) }

    e_triangle = { TA: negy,
                   TB: posx,
                   TC: negx }

    f_triangle = { TA: posx,
                   TB: posy,
                   TC: negx }

    mesh.append((compute_normal(a_triangle), a_triangle))
    mesh.append((compute_normal(b_triangle), b_triangle))
    mesh.append((compute_normal(c_triangle), c_triangle))
    mesh.append((compute_normal(d_triangle), d_triangle))
    mesh.append((compute_normal(e_triangle), e_triangle))
    mesh.append((compute_normal(f_triangle), f_triangle))