#include <Python.h>
#include <string.h>

// Fonction utilitaire pour rotation d'une face 3x3 dans le sens horaire
static void rotate_face_clockwise(char* face, char* result) {
    result[0] = face[6]; result[1] = face[3]; result[2] = face[0];
    result[3] = face[7]; result[4] = face[4]; result[5] = face[1];
    result[6] = face[8]; result[7] = face[5]; result[8] = face[2];
}

// Fonction utilitaire pour rotation d'une face 3x3 dans le sens anti-horaire
static void rotate_face_counterclockwise(char* face, char* result) {
    result[0] = face[2]; result[1] = face[5]; result[2] = face[8];
    result[3] = face[1]; result[4] = face[4]; result[5] = face[7];
    result[6] = face[0]; result[7] = face[3]; result[8] = face[6];
}

// Fonction principale de rotation d'un mouvement
static PyObject* rotate_move(PyObject* self, PyObject* args) {
    const char* state;
    const char* move;

    if (!PyArg_ParseTuple(args, "ss", &state, &move)) {
        return NULL;
    }

    // Vérifier que l'état fait 54 caractères
    if (strlen(state) != 54) {
        PyErr_SetString(PyExc_ValueError, "State must be 54 characters long");
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

            // Pour les mouvements M, S, E, x, y, z, on peut les ajouter si nécessaire
            // Ici je me concentre sur les mouvements de base U, R, F, D, L, B

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
