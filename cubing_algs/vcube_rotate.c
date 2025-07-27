#include <Python.h>
#include <string.h>

// Fonction utilitaire pour rotation d'une face 3x3 dans le sens horaire
static void rotate_face_clockwise(char* face, char* result) {
    result[0] = face[6]; result[1] = face[3]; result[2] = face[0];
    result[3] = face[7]; result[4] = face[4]; result[5] = face[1];
    result[6] = face[8]; result[7] = face[5]; result[8] = face[2];
}

// Fonction principale de rotation d'un mouvement
static PyObject* rotate_move(PyObject* self, PyObject* args) {
    const char* state;
    const char* move;

    if (!PyArg_ParseTuple(args, "ss", &state, &move)) {
        return NULL;
    }

    // Copier l'état pour modification
    char new_state[55];
    strcpy(new_state, state);

    // Parser le mouvement
    char face = move[0];
    int direction = 1; // Par défaut: sens horaire

    if (strlen(move) > 1) {
        if (move[1] == '\'') {
            direction = 3; // Anti-horaire = 3 rotations horaires
        } else if (move[1] == '2') {
            direction = 2; // 180° = 2 rotations horaires
        } else {
          PyErr_SetString(PyExc_ValueError, "Invalid move modifier");
            return NULL;
        }
    }

    // Effectuer les rotations
    for (int i = 0; i < direction; i++) {
        switch (face) {
            case 'U': {
                // Rotation U: les rangées du haut des 4 faces latérales tournent
                char f_top[3] = {new_state[18], new_state[19], new_state[20]};
                char r_top[3] = {new_state[9], new_state[10], new_state[11]};
                char b_top[3] = {new_state[45], new_state[46], new_state[47]};
                char l_top[3] = {new_state[36], new_state[37], new_state[38]};

                // Rotation de la face U
                char u_face[9];
                for (int j = 0; j < 9; j++) u_face[j] = new_state[j];
                char rotated_u[9];
                rotate_face_clockwise(u_face, rotated_u);

                // Mise à jour de l'état
                for (int j = 0; j < 9; j++) new_state[j] = rotated_u[j];

                // Rotation des rangées du haut
                new_state[9] = b_top[0]; new_state[10] = b_top[1]; new_state[11] = b_top[2];
                new_state[18] = r_top[0]; new_state[19] = r_top[1]; new_state[20] = r_top[2];
                new_state[36] = f_top[0]; new_state[37] = f_top[1]; new_state[38] = f_top[2];
                new_state[45] = l_top[0]; new_state[46] = l_top[1]; new_state[47] = l_top[2];
                break;
            }

            case 'R': {
                // Rotation R
                char u_right[3] = {new_state[2], new_state[5], new_state[8]};
                char f_right[3] = {new_state[20], new_state[23], new_state[26]};
                char d_right[3] = {new_state[29], new_state[32], new_state[35]};
                char b_left[3] = {new_state[45], new_state[48], new_state[51]};

                // Rotation de la face R
                char r_face[9];
                for (int j = 0; j < 9; j++) r_face[j] = new_state[9 + j];
                char rotated_r[9];
                rotate_face_clockwise(r_face, rotated_r);
                for (int j = 0; j < 9; j++) new_state[9 + j] = rotated_r[j];

                // Rotation des colonnes
                new_state[2] = f_right[0]; new_state[5] = f_right[1]; new_state[8] = f_right[2];
                new_state[20] = d_right[0]; new_state[23] = d_right[1]; new_state[26] = d_right[2];
                new_state[29] = b_left[2]; new_state[32] = b_left[1]; new_state[35] = b_left[0];
                new_state[45] = u_right[2]; new_state[48] = u_right[1]; new_state[51] = u_right[0];
                break;
            }

            case 'F': {
                // Rotation F
                char u_bottom[3] = {new_state[6], new_state[7], new_state[8]};
                char r_left[3] = {new_state[9], new_state[12], new_state[15]};
                char d_top[3] = {new_state[27], new_state[28], new_state[29]};
                char l_right[3] = {new_state[38], new_state[41], new_state[44]};

                // Rotation de la face F
                char f_face[9];
                for (int j = 0; j < 9; j++) f_face[j] = new_state[18 + j];
                char rotated_f[9];
                rotate_face_clockwise(f_face, rotated_f);
                for (int j = 0; j < 9; j++) new_state[18 + j] = rotated_f[j];

                // Rotation des éléments affectés
                new_state[6] = l_right[2]; new_state[7] = l_right[1]; new_state[8] = l_right[0];
                new_state[9] = u_bottom[0]; new_state[12] = u_bottom[1]; new_state[15] = u_bottom[2];
                new_state[27] = r_left[2]; new_state[28] = r_left[1]; new_state[29] = r_left[0];
                new_state[38] = d_top[0]; new_state[41] = d_top[1]; new_state[44] = d_top[2];
                break;
            }

            case 'D': {
                // Rotation D
                char f_bottom[3] = {new_state[24], new_state[25], new_state[26]};
                char r_bottom[3] = {new_state[15], new_state[16], new_state[17]};
                char b_bottom[3] = {new_state[51], new_state[52], new_state[53]};
                char l_bottom[3] = {new_state[42], new_state[43], new_state[44]};

                // Rotation de la face D
                char d_face[9];
                for (int j = 0; j < 9; j++) d_face[j] = new_state[27 + j];
                char rotated_d[9];
                rotate_face_clockwise(d_face, rotated_d);
                for (int j = 0; j < 9; j++) new_state[27 + j] = rotated_d[j];

                // Rotation des rangées du bas
                new_state[24] = l_bottom[0]; new_state[25] = l_bottom[1]; new_state[26] = l_bottom[2];
                new_state[15] = f_bottom[0]; new_state[16] = f_bottom[1]; new_state[17] = f_bottom[2];
                new_state[51] = r_bottom[0]; new_state[52] = r_bottom[1]; new_state[53] = r_bottom[2];
                new_state[42] = b_bottom[0]; new_state[43] = b_bottom[1]; new_state[44] = b_bottom[2];
                break;
            }

            case 'L': {
                // Rotation L
                char u_left[3] = {new_state[0], new_state[3], new_state[6]};
                char f_left[3] = {new_state[18], new_state[21], new_state[24]};
                char d_left[3] = {new_state[27], new_state[30], new_state[33]};
                char b_right[3] = {new_state[47], new_state[50], new_state[53]};

                // Rotation de la face L
                char l_face[9];
                for (int j = 0; j < 9; j++) l_face[j] = new_state[36 + j];
                char rotated_l[9];
                rotate_face_clockwise(l_face, rotated_l);
                for (int j = 0; j < 9; j++) new_state[36 + j] = rotated_l[j];

                // Rotation des colonnes
                new_state[0] = b_right[2]; new_state[3] = b_right[1]; new_state[6] = b_right[0];
                new_state[18] = u_left[0]; new_state[21] = u_left[1]; new_state[24] = u_left[2];
                new_state[27] = f_left[0]; new_state[30] = f_left[1]; new_state[33] = f_left[2];
                new_state[47] = d_left[2]; new_state[50] = d_left[1]; new_state[53] = d_left[0];
                break;
            }

            case 'B': {
                // Rotation B
                char u_top[3] = {new_state[0], new_state[1], new_state[2]};
                char r_right[3] = {new_state[11], new_state[14], new_state[17]};
                char d_bottom[3] = {new_state[33], new_state[34], new_state[35]};
                char l_left[3] = {new_state[36], new_state[39], new_state[42]};

                // Rotation de la face B
                char b_face[9];
                for (int j = 0; j < 9; j++) b_face[j] = new_state[45 + j];
                char rotated_b[9];
                rotate_face_clockwise(b_face, rotated_b);
                for (int j = 0; j < 9; j++) new_state[45 + j] = rotated_b[j];

                // Rotation des éléments affectés
                new_state[0] = r_right[0]; new_state[1] = r_right[1]; new_state[2] = r_right[2];
                new_state[11] = d_bottom[2]; new_state[14] = d_bottom[1]; new_state[17] = d_bottom[0];
                new_state[33] = l_left[0]; new_state[34] = l_left[1]; new_state[35] = l_left[2];
                new_state[36] = u_top[2]; new_state[39] = u_top[1]; new_state[42] = u_top[0];
                break;
            }

            case 'M': {
                // M est la tranche du milieu entre L et R (même direction que L)
                char u_middle[3] = {new_state[1], new_state[4], new_state[7]};
                char f_middle[3] = {new_state[19], new_state[22], new_state[25]};
                char d_middle[3] = {new_state[28], new_state[31], new_state[34]};
                char b_middle[3] = {new_state[46], new_state[49], new_state[52]};

                // Rotation (comme L)
                new_state[1] = b_middle[2]; new_state[4] = b_middle[1]; new_state[7] = b_middle[0];
                new_state[19] = u_middle[0]; new_state[22] = u_middle[1]; new_state[25] = u_middle[2];
                new_state[28] = f_middle[0]; new_state[31] = f_middle[1]; new_state[34] = f_middle[2];
                new_state[46] = d_middle[2]; new_state[49] = d_middle[1]; new_state[52] = d_middle[0];
                break;
            }

            case 'S': {
                // S est la tranche du milieu entre F et B (même direction que F)
                char u_middle[3] = {new_state[3], new_state[4], new_state[5]};
                char r_middle[3] = {new_state[10], new_state[13], new_state[16]};
                char d_middle[3] = {new_state[30], new_state[31], new_state[32]};
                char l_middle[3] = {new_state[37], new_state[40], new_state[43]};

                // Rotation (comme F)
                new_state[3] = l_middle[2]; new_state[4] = l_middle[1]; new_state[5] = l_middle[0];
                new_state[10] = u_middle[0]; new_state[13] = u_middle[1]; new_state[16] = u_middle[2];
                new_state[30] = r_middle[2]; new_state[31] = r_middle[1]; new_state[32] = r_middle[0];
                new_state[37] = d_middle[0]; new_state[40] = d_middle[1]; new_state[43] = d_middle[2];
                break;
            }

            case 'E': {
                // E est la tranche du milieu entre U et D (même direction que D)
                char f_middle[3] = {new_state[21], new_state[22], new_state[23]};
                char r_middle[3] = {new_state[12], new_state[13], new_state[14]};
                char b_middle[3] = {new_state[48], new_state[49], new_state[50]};
                char l_middle[3] = {new_state[39], new_state[40], new_state[41]};

                // Rotation (comme D)
                new_state[21] = l_middle[0]; new_state[22] = l_middle[1]; new_state[23] = l_middle[2];
                new_state[12] = f_middle[0]; new_state[13] = f_middle[1]; new_state[14] = f_middle[2];
                new_state[48] = r_middle[0]; new_state[49] = r_middle[1]; new_state[50] = r_middle[2];
                new_state[39] = b_middle[0]; new_state[40] = b_middle[1]; new_state[41] = b_middle[2];
                break;
            }

            case 'x': {
                // x est la rotation de tout le cube autour de l'axe x
                // (même que R, avec M' et L' ensemble)
                char temp_state[55];
                strcpy(temp_state, new_state);

                // Extraire toutes les faces
                char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
                for (int j = 0; j < 9; j++) {
                    u_face[j] = temp_state[j];
                    r_face[j] = temp_state[9 + j];
                    f_face[j] = temp_state[18 + j];
                    d_face[j] = temp_state[27 + j];
                    l_face[j] = temp_state[36 + j];
                    b_face[j] = temp_state[45 + j];
                }

                // Rotation de la face R
                char r_rotated[9];
                rotate_face_clockwise(r_face, r_rotated);

                // Rotation de la face L (anti-horaire)
                char l_rotated[9];
                l_rotated[0] = l_face[2]; l_rotated[1] = l_face[5]; l_rotated[2] = l_face[8];
                l_rotated[3] = l_face[1]; l_rotated[4] = l_face[4]; l_rotated[5] = l_face[7];
                l_rotated[6] = l_face[0]; l_rotated[7] = l_face[3]; l_rotated[8] = l_face[6];

                // Mise à jour de l'état
                for (int j = 0; j < 9; j++) {
                    new_state[j] = f_face[j];        // U devient F
                    new_state[9 + j] = r_rotated[j]; // R reste R mais tourne
                    new_state[18 + j] = d_face[j];   // F devient D
                    new_state[27 + j] = b_face[8-j]; // D devient B inversé
                    new_state[36 + j] = l_rotated[j]; // L reste L mais tourne
                    new_state[45 + j] = u_face[8-j]; // B devient U inversé
                }
                break;
            }

            case 'y': {
                // y est la rotation de tout le cube autour de l'axe y
                // (même que U, avec E' et D' ensemble)
                char temp_state[55];
                strcpy(temp_state, new_state);

                // Extraire toutes les faces
                char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
                for (int j = 0; j < 9; j++) {
                    u_face[j] = temp_state[j];
                    r_face[j] = temp_state[9 + j];
                    f_face[j] = temp_state[18 + j];
                    d_face[j] = temp_state[27 + j];
                    l_face[j] = temp_state[36 + j];
                    b_face[j] = temp_state[45 + j];
                }

                // Rotation de la face U
                char u_rotated[9];
                rotate_face_clockwise(u_face, u_rotated);

                // Rotation de la face D (anti-horaire)
                char d_rotated[9];
                d_rotated[0] = d_face[2]; d_rotated[1] = d_face[5]; d_rotated[2] = d_face[8];
                d_rotated[3] = d_face[1]; d_rotated[4] = d_face[4]; d_rotated[5] = d_face[7];
                d_rotated[6] = d_face[0]; d_rotated[7] = d_face[3]; d_rotated[8] = d_face[6];

                // Mise à jour de l'état
                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];     // U reste U mais tourne
                    new_state[9 + j] = b_face[j];    // R devient B
                    new_state[18 + j] = r_face[j];   // F devient R
                    new_state[27 + j] = d_rotated[j]; // D reste D mais tourne
                    new_state[36 + j] = f_face[j];   // L devient F
                    new_state[45 + j] = l_face[j];   // B devient L
                }
                break;
            }

            case 'z': {
                // z est la rotation de tout le cube autour de l'axe z
                // (même que F, avec S et B' ensemble)
                char temp_state[55];
                strcpy(temp_state, new_state);

                // Extraire toutes les faces
                char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
                for (int j = 0; j < 9; j++) {
                    u_face[j] = temp_state[j];
                    r_face[j] = temp_state[9 + j];
                    f_face[j] = temp_state[18 + j];
                    d_face[j] = temp_state[27 + j];
                    l_face[j] = temp_state[36 + j];
                    b_face[j] = temp_state[45 + j];
                }

                // Rotation de la face F
                char f_rotated[9];
                rotate_face_clockwise(f_face, f_rotated);

                // Rotation de la face B (anti-horaire)
                char b_rotated[9];
                b_rotated[0] = b_face[2]; b_rotated[1] = b_face[5]; b_rotated[2] = b_face[8];
                b_rotated[3] = b_face[1]; b_rotated[4] = b_face[4]; b_rotated[5] = b_face[7];
                b_rotated[6] = b_face[0]; b_rotated[7] = b_face[3]; b_rotated[8] = b_face[6];

                // Transformation des autres faces (elles tournent en changeant de position)
                char u_transformed[9], r_transformed[9], d_transformed[9], l_transformed[9];
                for (int j = 0; j < 9; j++) {
                    // Chaque face tourne de 90° en sens horaire quand elle change de position
                    u_transformed[j] = u_face[6 - 3*(j%3) + j/3];
                    r_transformed[j] = r_face[6 - 3*(j%3) + j/3];
                    d_transformed[j] = d_face[6 - 3*(j%3) + j/3];
                    l_transformed[j] = l_face[6 - 3*(j%3) + j/3];
                }

                // Mise à jour de l'état
                for (int j = 0; j < 9; j++) {
                    new_state[j] = l_transformed[j];     // U devient L
                    new_state[9 + j] = u_transformed[j]; // R devient U
                    new_state[18 + j] = f_rotated[j];    // F reste F mais tourne
                    new_state[27 + j] = r_transformed[j]; // D devient R
                    new_state[36 + j] = d_transformed[j]; // L devient D
                    new_state[45 + j] = b_rotated[j];    // B reste B mais tourne anti-horaire
                }
                break;
            }

            default:
                PyErr_SetString(PyExc_ValueError, "Invalid move face");
                return NULL;
        }
    }

    return PyUnicode_FromString(new_state);
}

// Définition des méthodes du module
static PyMethodDef VCubeRotateMethods[] = {
    {"rotate_move", rotate_move, METH_VARARGS, "Rotate cube state with given move"},
    {NULL, NULL, 0, NULL}
};

// Définition du module
static struct PyModuleDef vcuberotatemodule = {
    PyModuleDef_HEAD_INIT,
    "vcube_rotate",
    "Fast cube rotation operations",
    -1,
    VCubeRotateMethods
};

// Fonction d'initialisation du module
PyMODINIT_FUNC PyInit_vcube_rotate(void) {
    return PyModule_Create(&vcuberotatemodule);
}
