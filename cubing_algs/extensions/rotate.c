#include <Python.h>
#include <string.h>

// Fonction utilitaire pour rotation d'une face 3x3 dans le sens horaire
static void rotate_face_clockwise(char* face, char* result) {
    result[0] = face[6]; result[1] = face[3]; result[2] = face[0];
    result[3] = face[7]; result[4] = face[4]; result[5] = face[1];
    result[6] = face[8]; result[7] = face[5]; result[8] = face[2];
}

static void rotate_face_180(char* face, char* result) {
    result[0] = face[8]; result[1] = face[7]; result[2] = face[6];
    result[3] = face[5]; result[4] = face[4]; result[5] = face[3];
    result[6] = face[2]; result[7] = face[1]; result[8] = face[0];
}

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

    // Copier l'état pour modification
    char new_state[55];
    strcpy(new_state, state);

    // Parser le mouvement
    char face = move[0];
    int direction = 1; // Par défaut: sens horaire

    if (strlen(move) > 1) {
        if (move[1] == '\'') {
            direction = 3; // Anti-horaire
        } else if (move[1] == '2') {
            direction = 2; // 180°
        } else {
            PyErr_Format(PyExc_ValueError, "Invalid move modifier: '%c'", move[1]);
            return NULL;
        }
    }

    switch (face) {
        case 'U': {
            // Sauvegarder les rangées du haut des 4 faces latérales
            char f_top[3] = {new_state[18], new_state[19], new_state[20]};
            char r_top[3] = {new_state[9], new_state[10], new_state[11]};
            char b_top[3] = {new_state[45], new_state[46], new_state[47]};
            char l_top[3] = {new_state[36], new_state[37], new_state[38]};

            // Rotation de la face U selon la direction
            char u_face[9];
            for (int j = 0; j < 9; j++) u_face[j] = new_state[j];
            char rotated_u[9];

            if (direction == 1) {
                rotate_face_clockwise(u_face, rotated_u);
                // Rotation des rangées du haut (sens horaire)
                new_state[9] = b_top[0]; new_state[10] = b_top[1]; new_state[11] = b_top[2];
                new_state[18] = r_top[0]; new_state[19] = r_top[1]; new_state[20] = r_top[2];
                new_state[36] = f_top[0]; new_state[37] = f_top[1]; new_state[38] = f_top[2];
                new_state[45] = l_top[0]; new_state[46] = l_top[1]; new_state[47] = l_top[2];
            } else if (direction == 2) {
                rotate_face_180(u_face, rotated_u);
                // Rotation 180° des rangées du haut
                new_state[9] = l_top[0]; new_state[10] = l_top[1]; new_state[11] = l_top[2];
                new_state[18] = b_top[0]; new_state[19] = b_top[1]; new_state[20] = b_top[2];
                new_state[36] = r_top[0]; new_state[37] = r_top[1]; new_state[38] = r_top[2];
                new_state[45] = f_top[0]; new_state[46] = f_top[1]; new_state[47] = f_top[2];
            } else { // direction == 3 (anti-horaire)
                rotate_face_counterclockwise(u_face, rotated_u);
                // Rotation des rangées du haut (sens anti-horaire)
                new_state[9] = f_top[0]; new_state[10] = f_top[1]; new_state[11] = f_top[2];
                new_state[18] = l_top[0]; new_state[19] = l_top[1]; new_state[20] = l_top[2];
                new_state[36] = b_top[0]; new_state[37] = b_top[1]; new_state[38] = b_top[2];
                new_state[45] = r_top[0]; new_state[46] = r_top[1]; new_state[47] = r_top[2];
            }

            // Mise à jour de la face U
            for (int j = 0; j < 9; j++) new_state[j] = rotated_u[j];
            break;
        }

        case 'R': {
            char u_right[3] = {new_state[2], new_state[5], new_state[8]};
            char f_right[3] = {new_state[20], new_state[23], new_state[26]};
            char d_right[3] = {new_state[29], new_state[32], new_state[35]};
            char b_left[3] = {new_state[45], new_state[48], new_state[51]};

            char r_face[9];
            for (int j = 0; j < 9; j++) r_face[j] = new_state[9 + j];
            char rotated_r[9];

            if (direction == 1) {
                rotate_face_clockwise(r_face, rotated_r);
                new_state[2] = f_right[0]; new_state[5] = f_right[1]; new_state[8] = f_right[2];
                new_state[20] = d_right[0]; new_state[23] = d_right[1]; new_state[26] = d_right[2];
                new_state[29] = b_left[2]; new_state[32] = b_left[1]; new_state[35] = b_left[0];
                new_state[45] = u_right[2]; new_state[48] = u_right[1]; new_state[51] = u_right[0];
            } else if (direction == 2) {
                rotate_face_180(r_face, rotated_r);
                new_state[2] = d_right[0]; new_state[5] = d_right[1]; new_state[8] = d_right[2];
                new_state[20] = b_left[2]; new_state[23] = b_left[1]; new_state[26] = b_left[0];
                new_state[29] = u_right[0]; new_state[32] = u_right[1]; new_state[35] = u_right[2];
                new_state[45] = f_right[2]; new_state[48] = f_right[1]; new_state[51] = f_right[0];
            } else {
                rotate_face_counterclockwise(r_face, rotated_r);
                new_state[2] = b_left[2]; new_state[5] = b_left[1]; new_state[8] = b_left[0];
                new_state[20] = u_right[0]; new_state[23] = u_right[1]; new_state[26] = u_right[2];
                new_state[29] = f_right[0]; new_state[32] = f_right[1]; new_state[35] = f_right[2];
                new_state[45] = d_right[2]; new_state[48] = d_right[1]; new_state[51] = d_right[0];
            }

            for (int j = 0; j < 9; j++) new_state[9 + j] = rotated_r[j];
            break;
        }

        // Similaire pour F, D, L, B...
        case 'F': {
            char u_bottom[3] = {new_state[6], new_state[7], new_state[8]};
            char r_left[3] = {new_state[9], new_state[12], new_state[15]};
            char d_top[3] = {new_state[27], new_state[28], new_state[29]};
            char l_right[3] = {new_state[38], new_state[41], new_state[44]};

            char f_face[9];
            for (int j = 0; j < 9; j++) f_face[j] = new_state[18 + j];
            char rotated_f[9];

            if (direction == 1) {
                rotate_face_clockwise(f_face, rotated_f);
                new_state[6] = l_right[2]; new_state[7] = l_right[1]; new_state[8] = l_right[0];
                new_state[9] = u_bottom[0]; new_state[12] = u_bottom[1]; new_state[15] = u_bottom[2];
                new_state[27] = r_left[2]; new_state[28] = r_left[1]; new_state[29] = r_left[0];
                new_state[38] = d_top[0]; new_state[41] = d_top[1]; new_state[44] = d_top[2];
            } else if (direction == 2) {
                rotate_face_180(f_face, rotated_f);
                new_state[6] = d_top[2]; new_state[7] = d_top[1]; new_state[8] = d_top[0];
                new_state[9] = l_right[2]; new_state[12] = l_right[1]; new_state[15] = l_right[0];
                new_state[27] = u_bottom[2]; new_state[28] = u_bottom[1]; new_state[29] = u_bottom[0];
                new_state[38] = r_left[2]; new_state[41] = r_left[1]; new_state[44] = r_left[0];
            } else {
                rotate_face_counterclockwise(f_face, rotated_f);
                new_state[6] = r_left[0]; new_state[7] = r_left[1]; new_state[8] = r_left[2];
                new_state[9] = d_top[2]; new_state[12] = d_top[1]; new_state[15] = d_top[0];
                new_state[27] = l_right[0]; new_state[28] = l_right[1]; new_state[29] = l_right[2];
                new_state[38] = u_bottom[2]; new_state[41] = u_bottom[1]; new_state[44] = u_bottom[0];
            }

            for (int j = 0; j < 9; j++) new_state[18 + j] = rotated_f[j];
            break;
        }

        case 'D': {
            char f_bottom[3] = {new_state[24], new_state[25], new_state[26]};
            char r_bottom[3] = {new_state[15], new_state[16], new_state[17]};
            char b_bottom[3] = {new_state[51], new_state[52], new_state[53]};
            char l_bottom[3] = {new_state[42], new_state[43], new_state[44]};

            char d_face[9];
            for (int j = 0; j < 9; j++) d_face[j] = new_state[27 + j];
            char rotated_d[9];

            if (direction == 1) {
                rotate_face_clockwise(d_face, rotated_d);
                new_state[24] = l_bottom[0]; new_state[25] = l_bottom[1]; new_state[26] = l_bottom[2];
                new_state[15] = f_bottom[0]; new_state[16] = f_bottom[1]; new_state[17] = f_bottom[2];
                new_state[51] = r_bottom[0]; new_state[52] = r_bottom[1]; new_state[53] = r_bottom[2];
                new_state[42] = b_bottom[0]; new_state[43] = b_bottom[1]; new_state[44] = b_bottom[2];
            } else if (direction == 2) {
                rotate_face_180(d_face, rotated_d);
                new_state[24] = b_bottom[0]; new_state[25] = b_bottom[1]; new_state[26] = b_bottom[2];
                new_state[15] = l_bottom[0]; new_state[16] = l_bottom[1]; new_state[17] = l_bottom[2];
                new_state[51] = f_bottom[0]; new_state[52] = f_bottom[1]; new_state[53] = f_bottom[2];
                new_state[42] = r_bottom[0]; new_state[43] = r_bottom[1]; new_state[44] = r_bottom[2];
            } else {
                rotate_face_counterclockwise(d_face, rotated_d);
                new_state[24] = r_bottom[0]; new_state[25] = r_bottom[1]; new_state[26] = r_bottom[2];
                new_state[15] = b_bottom[0]; new_state[16] = b_bottom[1]; new_state[17] = b_bottom[2];
                new_state[51] = l_bottom[0]; new_state[52] = l_bottom[1]; new_state[53] = l_bottom[2];
                new_state[42] = f_bottom[0]; new_state[43] = f_bottom[1]; new_state[44] = f_bottom[2];
            }

            for (int j = 0; j < 9; j++) new_state[27 + j] = rotated_d[j];
            break;
        }

        case 'L': {
            char u_left[3] = {new_state[0], new_state[3], new_state[6]};
            char f_left[3] = {new_state[18], new_state[21], new_state[24]};
            char d_left[3] = {new_state[27], new_state[30], new_state[33]};
            char b_right[3] = {new_state[47], new_state[50], new_state[53]};

            char l_face[9];
            for (int j = 0; j < 9; j++) l_face[j] = new_state[36 + j];
            char rotated_l[9];

            if (direction == 1) {
                rotate_face_clockwise(l_face, rotated_l);
                new_state[0] = b_right[2]; new_state[3] = b_right[1]; new_state[6] = b_right[0];
                new_state[18] = u_left[0]; new_state[21] = u_left[1]; new_state[24] = u_left[2];
                new_state[27] = f_left[0]; new_state[30] = f_left[1]; new_state[33] = f_left[2];
                new_state[47] = d_left[2]; new_state[50] = d_left[1]; new_state[53] = d_left[0];
            } else if (direction == 2) {
                rotate_face_180(l_face, rotated_l);
                new_state[0] = d_left[0]; new_state[3] = d_left[1]; new_state[6] = d_left[2];
                new_state[18] = b_right[2]; new_state[21] = b_right[1]; new_state[24] = b_right[0];
                new_state[27] = u_left[0]; new_state[30] = u_left[1]; new_state[33] = u_left[2];
                new_state[47] = f_left[2]; new_state[50] = f_left[1]; new_state[53] = f_left[0];
            } else {
                rotate_face_counterclockwise(l_face, rotated_l);
                new_state[0] = f_left[0]; new_state[3] = f_left[1]; new_state[6] = f_left[2];
                new_state[18] = d_left[0]; new_state[21] = d_left[1]; new_state[24] = d_left[2];
                new_state[27] = b_right[2]; new_state[30] = b_right[1]; new_state[33] = b_right[0];
                new_state[47] = u_left[2]; new_state[50] = u_left[1]; new_state[53] = u_left[0];
            }

            for (int j = 0; j < 9; j++) new_state[36 + j] = rotated_l[j];
            break;
        }

        case 'B': {
            char u_top[3] = {new_state[0], new_state[1], new_state[2]};
            char r_right[3] = {new_state[11], new_state[14], new_state[17]};
            char d_bottom[3] = {new_state[33], new_state[34], new_state[35]};
            char l_left[3] = {new_state[36], new_state[39], new_state[42]};

            char b_face[9];
            for (int j = 0; j < 9; j++) b_face[j] = new_state[45 + j];
            char rotated_b[9];

            if (direction == 1) {
                rotate_face_clockwise(b_face, rotated_b);
                new_state[0] = r_right[0]; new_state[1] = r_right[1]; new_state[2] = r_right[2];
                new_state[11] = d_bottom[2]; new_state[14] = d_bottom[1]; new_state[17] = d_bottom[0];
                new_state[33] = l_left[0]; new_state[34] = l_left[1]; new_state[35] = l_left[2];
                new_state[36] = u_top[2]; new_state[39] = u_top[1]; new_state[42] = u_top[0];
            } else if (direction == 2) {
                rotate_face_180(b_face, rotated_b);
                new_state[0] = d_bottom[2]; new_state[1] = d_bottom[1]; new_state[2] = d_bottom[0];
                new_state[11] = l_left[2]; new_state[14] = l_left[1]; new_state[17] = l_left[0];
                new_state[33] = u_top[2]; new_state[34] = u_top[1]; new_state[35] = u_top[0];
                new_state[36] = r_right[2]; new_state[39] = r_right[1]; new_state[42] = r_right[0];
            } else {
                rotate_face_counterclockwise(b_face, rotated_b);
                new_state[0] = l_left[2]; new_state[1] = l_left[1]; new_state[2] = l_left[0];
                new_state[11] = u_top[0]; new_state[14] = u_top[1]; new_state[17] = u_top[2];
                new_state[33] = r_right[2]; new_state[34] = r_right[1]; new_state[35] = r_right[0];
                new_state[36] = d_bottom[0]; new_state[39] = d_bottom[1]; new_state[42] = d_bottom[2];
            }

            for (int j = 0; j < 9; j++) new_state[45 + j] = rotated_b[j];
            break;
        }

        case 'M': {
            // M est la tranche du milieu entre L et R (même direction que L)
            char u_middle[3] = {new_state[1], new_state[4], new_state[7]};
            char f_middle[3] = {new_state[19], new_state[22], new_state[25]};
            char d_middle[3] = {new_state[28], new_state[31], new_state[34]};
            char b_middle[3] = {new_state[46], new_state[49], new_state[52]};

            if (direction == 1) {
                new_state[1] = b_middle[2]; new_state[4] = b_middle[1]; new_state[7] = b_middle[0];
                new_state[19] = u_middle[0]; new_state[22] = u_middle[1]; new_state[25] = u_middle[2];
                new_state[28] = f_middle[0]; new_state[31] = f_middle[1]; new_state[34] = f_middle[2];
                new_state[46] = d_middle[2]; new_state[49] = d_middle[1]; new_state[52] = d_middle[0];
            } else if (direction == 2) {
                new_state[1] = d_middle[0]; new_state[4] = d_middle[1]; new_state[7] = d_middle[2];
                new_state[19] = b_middle[2]; new_state[22] = b_middle[1]; new_state[25] = b_middle[0];
                new_state[28] = u_middle[0]; new_state[31] = u_middle[1]; new_state[34] = u_middle[2];
                new_state[46] = f_middle[2]; new_state[49] = f_middle[1]; new_state[52] = f_middle[0];
            } else {
                new_state[1] = f_middle[0]; new_state[4] = f_middle[1]; new_state[7] = f_middle[2];
                new_state[19] = d_middle[0]; new_state[22] = d_middle[1]; new_state[25] = d_middle[2];
                new_state[28] = b_middle[2]; new_state[31] = b_middle[1]; new_state[34] = b_middle[0];
                new_state[46] = u_middle[2]; new_state[49] = u_middle[1]; new_state[52] = u_middle[0];
            }
            break;
        }

        case 'S': {
            // S est la tranche du milieu entre F et B (même direction que F)
            char u_middle[3] = {new_state[3], new_state[4], new_state[5]};
            char r_middle[3] = {new_state[10], new_state[13], new_state[16]};
            char d_middle[3] = {new_state[30], new_state[31], new_state[32]};
            char l_middle[3] = {new_state[37], new_state[40], new_state[43]};

            if (direction == 1) {
                new_state[3] = l_middle[2]; new_state[4] = l_middle[1]; new_state[5] = l_middle[0];
                new_state[10] = u_middle[0]; new_state[13] = u_middle[1]; new_state[16] = u_middle[2];
                new_state[30] = r_middle[2]; new_state[31] = r_middle[1]; new_state[32] = r_middle[0];
                new_state[37] = d_middle[0]; new_state[40] = d_middle[1]; new_state[43] = d_middle[2];
            } else if (direction == 2) {
                new_state[3] = d_middle[2]; new_state[4] = d_middle[1]; new_state[5] = d_middle[0];
                new_state[10] = l_middle[2]; new_state[13] = l_middle[1]; new_state[16] = l_middle[0];
                new_state[30] = u_middle[2]; new_state[31] = u_middle[1]; new_state[32] = u_middle[0];
                new_state[37] = r_middle[2]; new_state[40] = r_middle[1]; new_state[43] = r_middle[0];
            } else {
                new_state[3] = r_middle[0]; new_state[4] = r_middle[1]; new_state[5] = r_middle[2];
                new_state[10] = d_middle[2]; new_state[13] = d_middle[1]; new_state[16] = d_middle[0];
                new_state[30] = l_middle[0]; new_state[31] = l_middle[1]; new_state[32] = l_middle[2];
                new_state[37] = u_middle[2]; new_state[40] = u_middle[1]; new_state[43] = u_middle[0];
            }
            break;
        }

        case 'E': {
            // E est la tranche du milieu entre U et D (même direction que D)
            char f_middle[3] = {new_state[21], new_state[22], new_state[23]};
            char r_middle[3] = {new_state[12], new_state[13], new_state[14]};
            char b_middle[3] = {new_state[48], new_state[49], new_state[50]};
            char l_middle[3] = {new_state[39], new_state[40], new_state[41]};

            if (direction == 1) {
                new_state[21] = l_middle[0]; new_state[22] = l_middle[1]; new_state[23] = l_middle[2];
                new_state[12] = f_middle[0]; new_state[13] = f_middle[1]; new_state[14] = f_middle[2];
                new_state[48] = r_middle[0]; new_state[49] = r_middle[1]; new_state[50] = r_middle[2];
                new_state[39] = b_middle[0]; new_state[40] = b_middle[1]; new_state[41] = b_middle[2];
            } else if (direction == 2) {
                new_state[21] = b_middle[0]; new_state[22] = b_middle[1]; new_state[23] = b_middle[2];
                new_state[12] = l_middle[0]; new_state[13] = l_middle[1]; new_state[14] = l_middle[2];
                new_state[48] = f_middle[0]; new_state[49] = f_middle[1]; new_state[50] = f_middle[2];
                new_state[39] = r_middle[0]; new_state[40] = r_middle[1]; new_state[41] = r_middle[2];
            } else {
                new_state[21] = r_middle[0]; new_state[22] = r_middle[1]; new_state[23] = r_middle[2];
                new_state[12] = b_middle[0]; new_state[13] = b_middle[1]; new_state[14] = b_middle[2];
                new_state[48] = l_middle[0]; new_state[49] = l_middle[1]; new_state[50] = l_middle[2];
                new_state[39] = f_middle[0]; new_state[40] = f_middle[1]; new_state[41] = f_middle[2];
            }
            break;
        }

        case 'x': {
            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = new_state[j];
                r_face[j] = new_state[9 + j];
                f_face[j] = new_state[18 + j];
                d_face[j] = new_state[27 + j];
                l_face[j] = new_state[36 + j];
                b_face[j] = new_state[45 + j];
            }

            if (direction == 1) {
                // x rotation: U<-F, R clockwise, F<-D, D<-B(inverted), L counter-clockwise, B<-U(inverted)
                // Based on expected permutations: 0<-18, 1<-19, 2<-20, etc.
                
                // U <- F (direct copy)
                new_state[0] = f_face[0];   // F[0] -> U[0] (position 18 -> 0)
                new_state[1] = f_face[1];   // F[1] -> U[1] (position 19 -> 1)
                new_state[2] = f_face[2];   // F[2] -> U[2] (position 20 -> 2)
                new_state[3] = f_face[3];   // F[3] -> U[3] (position 21 -> 3)
                new_state[4] = f_face[4];   // F[4] -> U[4] (position 22 -> 4)
                new_state[5] = f_face[5];   // F[5] -> U[5] (position 23 -> 5)
                new_state[6] = f_face[6];   // F[6] -> U[6] (position 24 -> 6)
                new_state[7] = f_face[7];   // F[7] -> U[7] (position 25 -> 7)
                new_state[8] = f_face[8];   // F[8] -> U[8] (position 26 -> 8)
                
                // R rotates clockwise: 9<-15, 10<-12, 11<-9, etc.
                new_state[9] = r_face[6];   // R[6] -> R[0] (position 15 -> 9)
                new_state[10] = r_face[3];  // R[3] -> R[1] (position 12 -> 10)
                new_state[11] = r_face[0];  // R[0] -> R[2] (position 9 -> 11)
                new_state[12] = r_face[7];  // R[7] -> R[3] (position 16 -> 12)
                new_state[13] = r_face[4];  // R[4] -> R[4] (position 13 -> 13)
                new_state[14] = r_face[1];  // R[1] -> R[5] (position 10 -> 14)
                new_state[15] = r_face[8];  // R[8] -> R[6] (position 17 -> 15)
                new_state[16] = r_face[5];  // R[5] -> R[7] (position 14 -> 16)
                new_state[17] = r_face[2];  // R[2] -> R[8] (position 11 -> 17)
                
                // F <- D (direct copy)
                new_state[18] = d_face[0];  // D[0] -> F[0] (position 27 -> 18)
                new_state[19] = d_face[1];  // D[1] -> F[1] (position 28 -> 19)
                new_state[20] = d_face[2];  // D[2] -> F[2] (position 29 -> 20)
                new_state[21] = d_face[3];  // D[3] -> F[3] (position 30 -> 21)
                new_state[22] = d_face[4];  // D[4] -> F[4] (position 31 -> 22)
                new_state[23] = d_face[5];  // D[5] -> F[5] (position 32 -> 23)
                new_state[24] = d_face[6];  // D[6] -> F[6] (position 33 -> 24)
                new_state[25] = d_face[7];  // D[7] -> F[7] (position 34 -> 25)
                new_state[26] = d_face[8];  // D[8] -> F[8] (position 35 -> 26)
                
                // D <- B (inverted): 27<-53, 28<-52, 29<-51, etc.
                new_state[27] = b_face[8];  // B[8] -> D[0] (position 53 -> 27)
                new_state[28] = b_face[7];  // B[7] -> D[1] (position 52 -> 28)
                new_state[29] = b_face[6];  // B[6] -> D[2] (position 51 -> 29)
                new_state[30] = b_face[5];  // B[5] -> D[3] (position 50 -> 30)
                new_state[31] = b_face[4];  // B[4] -> D[4] (position 49 -> 31)
                new_state[32] = b_face[3];  // B[3] -> D[5] (position 48 -> 32)
                new_state[33] = b_face[2];  // B[2] -> D[6] (position 47 -> 33)
                new_state[34] = b_face[1];  // B[1] -> D[7] (position 46 -> 34)
                new_state[35] = b_face[0];  // B[0] -> D[8] (position 45 -> 35)
                
                // L rotates counter-clockwise: 36<-38, 37<-41, 38<-44, etc.
                new_state[36] = l_face[2];  // L[2] -> L[0] (position 38 -> 36)
                new_state[37] = l_face[5];  // L[5] -> L[1] (position 41 -> 37)
                new_state[38] = l_face[8];  // L[8] -> L[2] (position 44 -> 38)
                new_state[39] = l_face[1];  // L[1] -> L[3] (position 37 -> 39)
                new_state[40] = l_face[4];  // L[4] -> L[4] (position 40 -> 40)
                new_state[41] = l_face[7];  // L[7] -> L[5] (position 43 -> 41)
                new_state[42] = l_face[0];  // L[0] -> L[6] (position 36 -> 42)
                new_state[43] = l_face[3];  // L[3] -> L[7] (position 39 -> 43)
                new_state[44] = l_face[6];  // L[6] -> L[8] (position 42 -> 44)
                
                // B <- U (inverted): 45<-8, 46<-7, 47<-6, etc.
                new_state[45] = u_face[8];  // U[8] -> B[0] (position 8 -> 45)
                new_state[46] = u_face[7];  // U[7] -> B[1] (position 7 -> 46)
                new_state[47] = u_face[6];  // U[6] -> B[2] (position 6 -> 47)
                new_state[48] = u_face[5];  // U[5] -> B[3] (position 5 -> 48)
                new_state[49] = u_face[4];  // U[4] -> B[4] (position 4 -> 49)
                new_state[50] = u_face[3];  // U[3] -> B[5] (position 3 -> 50)
                new_state[51] = u_face[2];  // U[2] -> B[6] (position 2 -> 51)
                new_state[52] = u_face[1];  // U[1] -> B[7] (position 1 -> 52)
                new_state[53] = u_face[0];  // U[0] -> B[8] (position 0 -> 53)
            } else if (direction == 2) {
                // x2 rotation: U<-D, R 180°, F<-B(inverted), D<-U, L 180°, B<-F(inverted)
                // Based on expected permutations: 0<-27, 1<-28, 2<-29, etc.
                
                // U <- D (direct copy)
                new_state[0] = d_face[0];   // D[0] -> U[0] (position 27 -> 0)
                new_state[1] = d_face[1];   // D[1] -> U[1] (position 28 -> 1)
                new_state[2] = d_face[2];   // D[2] -> U[2] (position 29 -> 2)
                new_state[3] = d_face[3];   // D[3] -> U[3] (position 30 -> 3)
                new_state[4] = d_face[4];   // D[4] -> U[4] (position 31 -> 4)
                new_state[5] = d_face[5];   // D[5] -> U[5] (position 32 -> 5)
                new_state[6] = d_face[6];   // D[6] -> U[6] (position 33 -> 6)
                new_state[7] = d_face[7];   // D[7] -> U[7] (position 34 -> 7)
                new_state[8] = d_face[8];   // D[8] -> U[8] (position 35 -> 8)
                
                // R rotates 180°: 9<-17, 10<-16, 11<-15, etc.
                new_state[9] = r_face[8];   // R[8] -> R[0] (position 17 -> 9)
                new_state[10] = r_face[7];  // R[7] -> R[1] (position 16 -> 10)
                new_state[11] = r_face[6];  // R[6] -> R[2] (position 15 -> 11)
                new_state[12] = r_face[5];  // R[5] -> R[3] (position 14 -> 12)
                new_state[13] = r_face[4];  // R[4] -> R[4] (position 13 -> 13)
                new_state[14] = r_face[3];  // R[3] -> R[5] (position 12 -> 14)
                new_state[15] = r_face[2];  // R[2] -> R[6] (position 11 -> 15)
                new_state[16] = r_face[1];  // R[1] -> R[7] (position 10 -> 16)
                new_state[17] = r_face[0];  // R[0] -> R[8] (position 9 -> 17)
                
                // F <- B (inverted): 18<-53, 19<-52, 20<-51, etc.
                new_state[18] = b_face[8];  // B[8] -> F[0] (position 53 -> 18)
                new_state[19] = b_face[7];  // B[7] -> F[1] (position 52 -> 19)
                new_state[20] = b_face[6];  // B[6] -> F[2] (position 51 -> 20)
                new_state[21] = b_face[5];  // B[5] -> F[3] (position 50 -> 21)
                new_state[22] = b_face[4];  // B[4] -> F[4] (position 49 -> 22)
                new_state[23] = b_face[3];  // B[3] -> F[5] (position 48 -> 23)
                new_state[24] = b_face[2];  // B[2] -> F[6] (position 47 -> 24)
                new_state[25] = b_face[1];  // B[1] -> F[7] (position 46 -> 25)
                new_state[26] = b_face[0];  // B[0] -> F[8] (position 45 -> 26)
                
                // D <- U (direct copy)
                new_state[27] = u_face[0];  // U[0] -> D[0] (position 0 -> 27)
                new_state[28] = u_face[1];  // U[1] -> D[1] (position 1 -> 28)
                new_state[29] = u_face[2];  // U[2] -> D[2] (position 2 -> 29)
                new_state[30] = u_face[3];  // U[3] -> D[3] (position 3 -> 30)
                new_state[31] = u_face[4];  // U[4] -> D[4] (position 4 -> 31)
                new_state[32] = u_face[5];  // U[5] -> D[5] (position 5 -> 32)
                new_state[33] = u_face[6];  // U[6] -> D[6] (position 6 -> 33)
                new_state[34] = u_face[7];  // U[7] -> D[7] (position 7 -> 34)
                new_state[35] = u_face[8];  // U[8] -> D[8] (position 8 -> 35)
                
                // L rotates 180°: 36<-44, 37<-43, 38<-42, etc.
                new_state[36] = l_face[8];  // L[8] -> L[0] (position 44 -> 36)
                new_state[37] = l_face[7];  // L[7] -> L[1] (position 43 -> 37)
                new_state[38] = l_face[6];  // L[6] -> L[2] (position 42 -> 38)
                new_state[39] = l_face[5];  // L[5] -> L[3] (position 41 -> 39)
                new_state[40] = l_face[4];  // L[4] -> L[4] (position 40 -> 40)
                new_state[41] = l_face[3];  // L[3] -> L[5] (position 39 -> 41)
                new_state[42] = l_face[2];  // L[2] -> L[6] (position 38 -> 42)
                new_state[43] = l_face[1];  // L[1] -> L[7] (position 37 -> 43)
                new_state[44] = l_face[0];  // L[0] -> L[8] (position 36 -> 44)
                
                // B <- F (inverted): 45<-26, 46<-25, 47<-24, etc.
                new_state[45] = f_face[8];  // F[8] -> B[0] (position 26 -> 45)
                new_state[46] = f_face[7];  // F[7] -> B[1] (position 25 -> 46)
                new_state[47] = f_face[6];  // F[6] -> B[2] (position 24 -> 47)
                new_state[48] = f_face[5];  // F[5] -> B[3] (position 23 -> 48)
                new_state[49] = f_face[4];  // F[4] -> B[4] (position 22 -> 49)
                new_state[50] = f_face[3];  // F[3] -> B[5] (position 21 -> 50)
                new_state[51] = f_face[2];  // F[2] -> B[6] (position 20 -> 51)
                new_state[52] = f_face[1];  // F[1] -> B[7] (position 19 -> 52)
                new_state[53] = f_face[0];  // F[0] -> B[8] (position 18 -> 53)
            } else {
                // x' rotation: U<-B(inverted), R counter-clockwise, F<-U, D<-F, L clockwise, B<-D(inverted)
                // Based on expected permutations: 0<-53, 1<-52, 2<-51, etc.
                
                // U <- B (inverted): 0<-53, 1<-52, 2<-51, etc.
                new_state[0] = b_face[8];   // B[8] -> U[0] (position 53 -> 0)
                new_state[1] = b_face[7];   // B[7] -> U[1] (position 52 -> 1)
                new_state[2] = b_face[6];   // B[6] -> U[2] (position 51 -> 2)
                new_state[3] = b_face[5];   // B[5] -> U[3] (position 50 -> 3)
                new_state[4] = b_face[4];   // B[4] -> U[4] (position 49 -> 4)
                new_state[5] = b_face[3];   // B[3] -> U[5] (position 48 -> 5)
                new_state[6] = b_face[2];   // B[2] -> U[6] (position 47 -> 6)
                new_state[7] = b_face[1];   // B[1] -> U[7] (position 46 -> 7)
                new_state[8] = b_face[0];   // B[0] -> U[8] (position 45 -> 8)
                
                // R rotates counter-clockwise: 9<-11, 10<-14, 11<-17, etc.
                new_state[9] = r_face[2];   // R[2] -> R[0] (position 11 -> 9)
                new_state[10] = r_face[5];  // R[5] -> R[1] (position 14 -> 10)
                new_state[11] = r_face[8];  // R[8] -> R[2] (position 17 -> 11)
                new_state[12] = r_face[1];  // R[1] -> R[3] (position 10 -> 12)
                new_state[13] = r_face[4];  // R[4] -> R[4] (position 13 -> 13)
                new_state[14] = r_face[7];  // R[7] -> R[5] (position 16 -> 14)
                new_state[15] = r_face[0];  // R[0] -> R[6] (position 9 -> 15)
                new_state[16] = r_face[3];  // R[3] -> R[7] (position 12 -> 16)
                new_state[17] = r_face[6];  // R[6] -> R[8] (position 15 -> 17)
                
                // F <- U (direct copy): 18<-0, 19<-1, 20<-2, etc.
                new_state[18] = u_face[0];  // U[0] -> F[0] (position 0 -> 18)
                new_state[19] = u_face[1];  // U[1] -> F[1] (position 1 -> 19)
                new_state[20] = u_face[2];  // U[2] -> F[2] (position 2 -> 20)
                new_state[21] = u_face[3];  // U[3] -> F[3] (position 3 -> 21)
                new_state[22] = u_face[4];  // U[4] -> F[4] (position 4 -> 22)
                new_state[23] = u_face[5];  // U[5] -> F[5] (position 5 -> 23)
                new_state[24] = u_face[6];  // U[6] -> F[6] (position 6 -> 24)
                new_state[25] = u_face[7];  // U[7] -> F[7] (position 7 -> 25)
                new_state[26] = u_face[8];  // U[8] -> F[8] (position 8 -> 26)
                
                // D <- F (direct copy): 27<-18, 28<-19, 29<-20, etc.
                new_state[27] = f_face[0];  // F[0] -> D[0] (position 18 -> 27)
                new_state[28] = f_face[1];  // F[1] -> D[1] (position 19 -> 28)
                new_state[29] = f_face[2];  // F[2] -> D[2] (position 20 -> 29)
                new_state[30] = f_face[3];  // F[3] -> D[3] (position 21 -> 30)
                new_state[31] = f_face[4];  // F[4] -> D[4] (position 22 -> 31)
                new_state[32] = f_face[5];  // F[5] -> D[5] (position 23 -> 32)
                new_state[33] = f_face[6];  // F[6] -> D[6] (position 24 -> 33)
                new_state[34] = f_face[7];  // F[7] -> D[7] (position 25 -> 34)
                new_state[35] = f_face[8];  // F[8] -> D[8] (position 26 -> 35)
                
                // L rotates clockwise: L follows same pattern as R clockwise
                new_state[36] = l_face[6];  // L[6] -> L[0]
                new_state[37] = l_face[3];  // L[3] -> L[1]
                new_state[38] = l_face[0];  // L[0] -> L[2]
                new_state[39] = l_face[7];  // L[7] -> L[3]
                new_state[40] = l_face[4];  // L[4] -> L[4]
                new_state[41] = l_face[1];  // L[1] -> L[5]
                new_state[42] = l_face[8];  // L[8] -> L[6]
                new_state[43] = l_face[5];  // L[5] -> L[7]
                new_state[44] = l_face[2];  // L[2] -> L[8]
                
                // B <- D (inverted): 45<-35, 46<-34, 47<-33, etc.
                new_state[45] = d_face[8];  // D[8] -> B[0] (position 35 -> 45)
                new_state[46] = d_face[7];  // D[7] -> B[1] (position 34 -> 46)
                new_state[47] = d_face[6];  // D[6] -> B[2] (position 33 -> 47)
                new_state[48] = d_face[5];  // D[5] -> B[3] (position 32 -> 48)
                new_state[49] = d_face[4];  // D[4] -> B[4] (position 31 -> 49)
                new_state[50] = d_face[3];  // D[3] -> B[5] (position 30 -> 50)
                new_state[51] = d_face[2];  // D[2] -> B[6] (position 29 -> 51)
                new_state[52] = d_face[1];  // D[1] -> B[7] (position 28 -> 52)
                new_state[53] = d_face[0];  // D[0] -> B[8] (position 27 -> 53)
            }
            break;
        }

        case 'y': {
            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = new_state[j];
                r_face[j] = new_state[9 + j];
                f_face[j] = new_state[18 + j];
                d_face[j] = new_state[27 + j];
                l_face[j] = new_state[36 + j];
                b_face[j] = new_state[45 + j];
            }

            if (direction == 1) {
                // y rotation: U clockwise, R<-B, F<-R, D counter-clockwise, L<-F, B<-L
                // Based on expected permutations: 0<-6, 1<-3, 2<-0, etc.
                
                // U rotates clockwise: 0<-6, 1<-3, 2<-0, etc.
                new_state[0] = u_face[6];   // U[6] -> U[0] (position 6 -> 0)
                new_state[1] = u_face[3];   // U[3] -> U[1] (position 3 -> 1)
                new_state[2] = u_face[0];   // U[0] -> U[2] (position 0 -> 2)
                new_state[3] = u_face[7];   // U[7] -> U[3] (position 7 -> 3)
                new_state[4] = u_face[4];   // U[4] -> U[4] (position 4 -> 4)
                new_state[5] = u_face[1];   // U[1] -> U[5] (position 1 -> 5)
                new_state[6] = u_face[8];   // U[8] -> U[6] (position 8 -> 6)
                new_state[7] = u_face[5];   // U[5] -> U[7] (position 5 -> 7)
                new_state[8] = u_face[2];   // U[2] -> U[8] (position 2 -> 8)
                
                // R <- B (direct copy): 9<-45, 10<-46, 11<-47, etc.
                new_state[9] = b_face[0];   // B[0] -> R[0] (position 45 -> 9)
                new_state[10] = b_face[1];  // B[1] -> R[1] (position 46 -> 10)
                new_state[11] = b_face[2];  // B[2] -> R[2] (position 47 -> 11)
                new_state[12] = b_face[3];  // B[3] -> R[3] (position 48 -> 12)
                new_state[13] = b_face[4];  // B[4] -> R[4] (position 49 -> 13)
                new_state[14] = b_face[5];  // B[5] -> R[5] (position 50 -> 14)
                new_state[15] = b_face[6];  // B[6] -> R[6] (position 51 -> 15)
                new_state[16] = b_face[7];  // B[7] -> R[7] (position 52 -> 16)
                new_state[17] = b_face[8];  // B[8] -> R[8] (position 53 -> 17)
                
                // F <- R (direct copy): 18<-9, 19<-10, 20<-11, etc.
                new_state[18] = r_face[0];  // R[0] -> F[0] (position 9 -> 18)
                new_state[19] = r_face[1];  // R[1] -> F[1] (position 10 -> 19)
                new_state[20] = r_face[2];  // R[2] -> F[2] (position 11 -> 20)
                new_state[21] = r_face[3];  // R[3] -> F[3] (position 12 -> 21)
                new_state[22] = r_face[4];  // R[4] -> F[4] (position 13 -> 22)
                new_state[23] = r_face[5];  // R[5] -> F[5] (position 14 -> 23)
                new_state[24] = r_face[6];  // R[6] -> F[6] (position 15 -> 24)
                new_state[25] = r_face[7];  // R[7] -> F[7] (position 16 -> 25)
                new_state[26] = r_face[8];  // R[8] -> F[8] (position 17 -> 26)
                
                // D rotates counter-clockwise: 27<-29, 28<-32, 29<-35, etc.
                new_state[27] = d_face[2];  // D[2] -> D[0] (position 29 -> 27)
                new_state[28] = d_face[5];  // D[5] -> D[1] (position 32 -> 28)
                new_state[29] = d_face[8];  // D[8] -> D[2] (position 35 -> 29)
                new_state[30] = d_face[1];  // D[1] -> D[3] (position 28 -> 30)
                new_state[31] = d_face[4];  // D[4] -> D[4] (position 31 -> 31)
                new_state[32] = d_face[7];  // D[7] -> D[5] (position 34 -> 32)
                new_state[33] = d_face[0];  // D[0] -> D[6] (position 27 -> 33)
                new_state[34] = d_face[3];  // D[3] -> D[7] (position 30 -> 34)
                new_state[35] = d_face[6];  // D[6] -> D[8] (position 33 -> 35)
                
                // L <- F (direct copy): 36<-18, 37<-19, 38<-20, etc.
                new_state[36] = f_face[0];  // F[0] -> L[0] (position 18 -> 36)
                new_state[37] = f_face[1];  // F[1] -> L[1] (position 19 -> 37)
                new_state[38] = f_face[2];  // F[2] -> L[2] (position 20 -> 38)
                new_state[39] = f_face[3];  // F[3] -> L[3] (position 21 -> 39)
                new_state[40] = f_face[4];  // F[4] -> L[4] (position 22 -> 40)
                new_state[41] = f_face[5];  // F[5] -> L[5] (position 23 -> 41)
                new_state[42] = f_face[6];  // F[6] -> L[6] (position 24 -> 42)
                new_state[43] = f_face[7];  // F[7] -> L[7] (position 25 -> 43)
                new_state[44] = f_face[8];  // F[8] -> L[8] (position 26 -> 44)
                
                // B <- L (direct copy): 45<-36, 46<-37, 47<-38, etc.
                new_state[45] = l_face[0];  // L[0] -> B[0] (position 36 -> 45)
                new_state[46] = l_face[1];  // L[1] -> B[1] (position 37 -> 46)
                new_state[47] = l_face[2];  // L[2] -> B[2] (position 38 -> 47)
                new_state[48] = l_face[3];  // L[3] -> B[3] (position 39 -> 48)
                new_state[49] = l_face[4];  // L[4] -> B[4] (position 40 -> 49)
                new_state[50] = l_face[5];  // L[5] -> B[5] (position 41 -> 50)
                new_state[51] = l_face[6];  // L[6] -> B[6] (position 42 -> 51)
                new_state[52] = l_face[7];  // L[7] -> B[7] (position 43 -> 52)
                new_state[53] = l_face[8];  // L[8] -> B[8] (position 44 -> 53)
            } else if (direction == 2) {
                // y2 rotation: U 180°, R<-L, F<-B, D 180°, L<-R, B<-F
                // Based on expected permutations: 0<-8, 1<-7, 2<-6, etc.
                
                // U rotates 180°: 0<-8, 1<-7, 2<-6, etc.
                new_state[0] = u_face[8];   // U[8] -> U[0] (position 8 -> 0)
                new_state[1] = u_face[7];   // U[7] -> U[1] (position 7 -> 1)
                new_state[2] = u_face[6];   // U[6] -> U[2] (position 6 -> 2)
                new_state[3] = u_face[5];   // U[5] -> U[3] (position 5 -> 3)
                new_state[4] = u_face[4];   // U[4] -> U[4] (position 4 -> 4)
                new_state[5] = u_face[3];   // U[3] -> U[5] (position 3 -> 5)
                new_state[6] = u_face[2];   // U[2] -> U[6] (position 2 -> 6)
                new_state[7] = u_face[1];   // U[1] -> U[7] (position 1 -> 7)
                new_state[8] = u_face[0];   // U[0] -> U[8] (position 0 -> 8)
                
                // R <- L (direct copy): 9<-36, 10<-37, 11<-38, etc.
                new_state[9] = l_face[0];   // L[0] -> R[0] (position 36 -> 9)
                new_state[10] = l_face[1];  // L[1] -> R[1] (position 37 -> 10)
                new_state[11] = l_face[2];  // L[2] -> R[2] (position 38 -> 11)
                new_state[12] = l_face[3];  // L[3] -> R[3] (position 39 -> 12)
                new_state[13] = l_face[4];  // L[4] -> R[4] (position 40 -> 13)
                new_state[14] = l_face[5];  // L[5] -> R[5] (position 41 -> 14)
                new_state[15] = l_face[6];  // L[6] -> R[6] (position 42 -> 15)
                new_state[16] = l_face[7];  // L[7] -> R[7] (position 43 -> 16)
                new_state[17] = l_face[8];  // L[8] -> R[8] (position 44 -> 17)
                
                // F <- B (direct copy): 18<-45, 19<-46, 20<-47, etc.
                new_state[18] = b_face[0];  // B[0] -> F[0] (position 45 -> 18)
                new_state[19] = b_face[1];  // B[1] -> F[1] (position 46 -> 19)
                new_state[20] = b_face[2];  // B[2] -> F[2] (position 47 -> 20)
                new_state[21] = b_face[3];  // B[3] -> F[3] (position 48 -> 21)
                new_state[22] = b_face[4];  // B[4] -> F[4] (position 49 -> 22)
                new_state[23] = b_face[5];  // B[5] -> F[5] (position 50 -> 23)
                new_state[24] = b_face[6];  // B[6] -> F[6] (position 51 -> 24)
                new_state[25] = b_face[7];  // B[7] -> F[7] (position 52 -> 25)
                new_state[26] = b_face[8];  // B[8] -> F[8] (position 53 -> 26)
                
                // D rotates 180°: 27<-35, 28<-34, 29<-33, etc.
                new_state[27] = d_face[8];  // D[8] -> D[0] (position 35 -> 27)
                new_state[28] = d_face[7];  // D[7] -> D[1] (position 34 -> 28)
                new_state[29] = d_face[6];  // D[6] -> D[2] (position 33 -> 29)
                new_state[30] = d_face[5];  // D[5] -> D[3] (position 32 -> 30)
                new_state[31] = d_face[4];  // D[4] -> D[4] (position 31 -> 31)
                new_state[32] = d_face[3];  // D[3] -> D[5] (position 30 -> 32)
                new_state[33] = d_face[2];  // D[2] -> D[6] (position 29 -> 33)
                new_state[34] = d_face[1];  // D[1] -> D[7] (position 28 -> 34)
                new_state[35] = d_face[0];  // D[0] -> D[8] (position 27 -> 35)
                
                // L <- R (direct copy): 36<-9, 37<-10, 38<-11, etc.
                new_state[36] = r_face[0];  // R[0] -> L[0] (position 9 -> 36)
                new_state[37] = r_face[1];  // R[1] -> L[1] (position 10 -> 37)
                new_state[38] = r_face[2];  // R[2] -> L[2] (position 11 -> 38)
                new_state[39] = r_face[3];  // R[3] -> L[3] (position 12 -> 39)
                new_state[40] = r_face[4];  // R[4] -> L[4] (position 13 -> 40)
                new_state[41] = r_face[5];  // R[5] -> L[5] (position 14 -> 41)
                new_state[42] = r_face[6];  // R[6] -> L[6] (position 15 -> 42)
                new_state[43] = r_face[7];  // R[7] -> L[7] (position 16 -> 43)
                new_state[44] = r_face[8];  // R[8] -> L[8] (position 17 -> 44)
                
                // B <- F (direct copy): 45<-18, 46<-19, 47<-20, etc.
                new_state[45] = f_face[0];  // F[0] -> B[0] (position 18 -> 45)
                new_state[46] = f_face[1];  // F[1] -> B[1] (position 19 -> 46)
                new_state[47] = f_face[2];  // F[2] -> B[2] (position 20 -> 47)
                new_state[48] = f_face[3];  // F[3] -> B[3] (position 21 -> 48)
                new_state[49] = f_face[4];  // F[4] -> B[4] (position 22 -> 49)
                new_state[50] = f_face[5];  // F[5] -> B[5] (position 23 -> 50)
                new_state[51] = f_face[6];  // F[6] -> B[6] (position 24 -> 51)
                new_state[52] = f_face[7];  // F[7] -> B[7] (position 25 -> 52)
                new_state[53] = f_face[8];  // F[8] -> B[8] (position 26 -> 53)
            } else {
                // y' rotation: U counter-clockwise, R<-F, F<-L, D clockwise, L<-B, B<-R
                // Based on expected permutations: 0<-2, 1<-5, 2<-8, etc.
                
                // U rotates counter-clockwise: 0<-2, 1<-5, 2<-8, etc.
                new_state[0] = u_face[2];   // U[2] -> U[0] (position 2 -> 0)
                new_state[1] = u_face[5];   // U[5] -> U[1] (position 5 -> 1)
                new_state[2] = u_face[8];   // U[8] -> U[2] (position 8 -> 2)
                new_state[3] = u_face[1];   // U[1] -> U[3] (position 1 -> 3)
                new_state[4] = u_face[4];   // U[4] -> U[4] (position 4 -> 4)
                new_state[5] = u_face[7];   // U[7] -> U[5] (position 7 -> 5)
                new_state[6] = u_face[0];   // U[0] -> U[6] (position 0 -> 6)
                new_state[7] = u_face[3];   // U[3] -> U[7] (position 3 -> 7)
                new_state[8] = u_face[6];   // U[6] -> U[8] (position 6 -> 8)
                
                // R <- F (direct copy): 9<-18, 10<-19, 11<-20, etc.
                new_state[9] = f_face[0];   // F[0] -> R[0] (position 18 -> 9)
                new_state[10] = f_face[1];  // F[1] -> R[1] (position 19 -> 10)
                new_state[11] = f_face[2];  // F[2] -> R[2] (position 20 -> 11)
                new_state[12] = f_face[3];  // F[3] -> R[3] (position 21 -> 12)
                new_state[13] = f_face[4];  // F[4] -> R[4] (position 22 -> 13)
                new_state[14] = f_face[5];  // F[5] -> R[5] (position 23 -> 14)
                new_state[15] = f_face[6];  // F[6] -> R[6] (position 24 -> 15)
                new_state[16] = f_face[7];  // F[7] -> R[7] (position 25 -> 16)
                new_state[17] = f_face[8];  // F[8] -> R[8] (position 26 -> 17)
                
                // F <- L (direct copy): 18<-36, 19<-37, 20<-38, etc.
                new_state[18] = l_face[0];  // L[0] -> F[0] (position 36 -> 18)
                new_state[19] = l_face[1];  // L[1] -> F[1] (position 37 -> 19)
                new_state[20] = l_face[2];  // L[2] -> F[2] (position 38 -> 20)
                new_state[21] = l_face[3];  // L[3] -> F[3] (position 39 -> 21)
                new_state[22] = l_face[4];  // L[4] -> F[4] (position 40 -> 22)
                new_state[23] = l_face[5];  // L[5] -> F[5] (position 41 -> 23)
                new_state[24] = l_face[6];  // L[6] -> F[6] (position 42 -> 24)
                new_state[25] = l_face[7];  // L[7] -> F[7] (position 43 -> 25)
                new_state[26] = l_face[8];  // L[8] -> F[8] (position 44 -> 26)
                
                // D rotates clockwise: 27<-33, 28<-30, 29<-27, etc.
                new_state[27] = d_face[6];  // D[6] -> D[0] (position 33 -> 27)
                new_state[28] = d_face[3];  // D[3] -> D[1] (position 30 -> 28)
                new_state[29] = d_face[0];  // D[0] -> D[2] (position 27 -> 29)
                new_state[30] = d_face[7];  // D[7] -> D[3] (position 34 -> 30)
                new_state[31] = d_face[4];  // D[4] -> D[4] (position 31 -> 31)
                new_state[32] = d_face[1];  // D[1] -> D[5] (position 28 -> 32)
                new_state[33] = d_face[8];  // D[8] -> D[6] (position 35 -> 33)
                new_state[34] = d_face[5];  // D[5] -> D[7] (position 32 -> 34)
                new_state[35] = d_face[2];  // D[2] -> D[8] (position 29 -> 35)
                
                // L <- B (direct copy): 36<-45, 37<-46, 38<-47, etc.
                new_state[36] = b_face[0];  // B[0] -> L[0] (position 45 -> 36)
                new_state[37] = b_face[1];  // B[1] -> L[1] (position 46 -> 37)
                new_state[38] = b_face[2];  // B[2] -> L[2] (position 47 -> 38)
                new_state[39] = b_face[3];  // B[3] -> L[3] (position 48 -> 39)
                new_state[40] = b_face[4];  // B[4] -> L[4] (position 49 -> 40)
                new_state[41] = b_face[5];  // B[5] -> L[5] (position 50 -> 41)
                new_state[42] = b_face[6];  // B[6] -> L[6] (position 51 -> 42)
                new_state[43] = b_face[7];  // B[7] -> L[7] (position 52 -> 43)
                new_state[44] = b_face[8];  // B[8] -> L[8] (position 53 -> 44)
                
                // B <- R (direct copy): 45<-9, 46<-10, 47<-11, etc.
                new_state[45] = r_face[0];  // R[0] -> B[0] (position 9 -> 45)
                new_state[46] = r_face[1];  // R[1] -> B[1] (position 10 -> 46)
                new_state[47] = r_face[2];  // R[2] -> B[2] (position 11 -> 47)
                new_state[48] = r_face[3];  // R[3] -> B[3] (position 12 -> 48)
                new_state[49] = r_face[4];  // R[4] -> B[4] (position 13 -> 49)
                new_state[50] = r_face[5];  // R[5] -> B[5] (position 14 -> 50)
                new_state[51] = r_face[6];  // R[6] -> B[6] (position 15 -> 51)
                new_state[52] = r_face[7];  // R[7] -> B[7] (position 16 -> 52)
                new_state[53] = r_face[8];  // R[8] -> B[8] (position 17 -> 53)
            }
            break;
        }

        case 'z': {
            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = new_state[j];
                r_face[j] = new_state[9 + j];
                f_face[j] = new_state[18 + j];
                d_face[j] = new_state[27 + j];
                l_face[j] = new_state[36 + j];
                b_face[j] = new_state[45 + j];
            }
            if (direction == 1) {
                // z rotation: U<-L, R<-U, F clockwise, D<-R, L<-D, B counter-clockwise  
                // Based on expected permutations: 0<-42, 1<-39, 2<-36, etc.
                
                // U <- L (with rotation: L positions that go to U)
                new_state[0] = l_face[6];  // L[6] -> U[0] (position 42 -> 0)
                new_state[1] = l_face[3];  // L[3] -> U[1] (position 39 -> 1)  
                new_state[2] = l_face[0];  // L[0] -> U[2] (position 36 -> 2)
                new_state[3] = l_face[7];  // L[7] -> U[3] (position 43 -> 3)
                new_state[4] = l_face[4];  // L[4] -> U[4] (position 40 -> 4)
                new_state[5] = l_face[1];  // L[1] -> U[5] (position 37 -> 5)
                new_state[6] = l_face[8];  // L[8] -> U[6] (position 44 -> 6)
                new_state[7] = l_face[5];  // L[5] -> U[7] (position 41 -> 7)
                new_state[8] = l_face[2];  // L[2] -> U[8] (position 38 -> 8)
                
                // R <- U (with rotation)
                new_state[9] = u_face[6];  // U[6] -> R[0] (position 6 -> 9)
                new_state[10] = u_face[3]; // U[3] -> R[1] (position 3 -> 10)
                new_state[11] = u_face[0]; // U[0] -> R[2] (position 0 -> 11)
                new_state[12] = u_face[7]; // U[7] -> R[3] (position 7 -> 12)
                new_state[13] = u_face[4]; // U[4] -> R[4] (position 4 -> 13)
                new_state[14] = u_face[1]; // U[1] -> R[5] (position 1 -> 14)
                new_state[15] = u_face[8]; // U[8] -> R[6] (position 8 -> 15)
                new_state[16] = u_face[5]; // U[5] -> R[7] (position 5 -> 16)
                new_state[17] = u_face[2]; // U[2] -> R[8] (position 2 -> 17)
                
                // F rotates clockwise
                new_state[18] = f_face[6]; // F[0] <- F[6]
                new_state[19] = f_face[3]; // F[1] <- F[3]
                new_state[20] = f_face[0]; // F[2] <- F[0]
                new_state[21] = f_face[7]; // F[3] <- F[7]
                new_state[22] = f_face[4]; // F[4] <- F[4]
                new_state[23] = f_face[1]; // F[5] <- F[1]
                new_state[24] = f_face[8]; // F[6] <- F[8]
                new_state[25] = f_face[5]; // F[7] <- F[5]
                new_state[26] = f_face[2]; // F[8] <- F[2]
                
                // D <- R (with rotation)
                new_state[27] = r_face[6]; // R[6] -> D[0] (position 15 -> 27)
                new_state[28] = r_face[3]; // R[3] -> D[1] (position 12 -> 28)
                new_state[29] = r_face[0]; // R[0] -> D[2] (position 9 -> 29)
                new_state[30] = r_face[7]; // R[7] -> D[3] (position 16 -> 30)
                new_state[31] = r_face[4]; // R[4] -> D[4] (position 13 -> 31)
                new_state[32] = r_face[1]; // R[1] -> D[5] (position 10 -> 32)
                new_state[33] = r_face[8]; // R[8] -> D[6] (position 17 -> 33)
                new_state[34] = r_face[5]; // R[5] -> D[7] (position 14 -> 34)
                new_state[35] = r_face[2]; // R[2] -> D[8] (position 11 -> 35)
                
                // L <- D (with rotation)
                new_state[36] = d_face[6]; // D[6] -> L[0] (position 33 -> 36)
                new_state[37] = d_face[3]; // D[3] -> L[1] (position 30 -> 37)
                new_state[38] = d_face[0]; // D[0] -> L[2] (position 27 -> 38)
                new_state[39] = d_face[7]; // D[7] -> L[3] (position 34 -> 39)
                new_state[40] = d_face[4]; // D[4] -> L[4] (position 31 -> 40)
                new_state[41] = d_face[1]; // D[1] -> L[5] (position 28 -> 41)
                new_state[42] = d_face[8]; // D[8] -> L[6] (position 35 -> 42)
                new_state[43] = d_face[5]; // D[5] -> L[7] (position 32 -> 43)
                new_state[44] = d_face[2]; // D[2] -> L[8] (position 29 -> 44)
                
                // B rotates counterclockwise 
                new_state[45] = b_face[2]; // B[0] <- B[2]
                new_state[46] = b_face[5]; // B[1] <- B[5]
                new_state[47] = b_face[8]; // B[2] <- B[8]
                new_state[48] = b_face[1]; // B[3] <- B[1]
                new_state[49] = b_face[4]; // B[4] <- B[4]
                new_state[50] = b_face[7]; // B[5] <- B[7]
                new_state[51] = b_face[0]; // B[6] <- B[0]
                new_state[52] = b_face[3]; // B[7] <- B[3]
                new_state[53] = b_face[6]; // B[8] <- B[6]
            } else if (direction == 2) {
                // z2 rotation: 180° rotation
                // U -> D (with 180° rotation: j -> 8-j)
                new_state[27] = u_face[8]; // U[0] -> D[0]
                new_state[28] = u_face[7]; // U[1] -> D[1]
                new_state[29] = u_face[6]; // U[2] -> D[2]
                new_state[30] = u_face[5]; // U[3] -> D[3]
                new_state[31] = u_face[4]; // U[4] -> D[4]
                new_state[32] = u_face[3]; // U[5] -> D[5]
                new_state[33] = u_face[2]; // U[6] -> D[6]
                new_state[34] = u_face[1]; // U[7] -> D[7]
                new_state[35] = u_face[0]; // U[8] -> D[8]
                
                // R -> L (with 180° rotation)
                new_state[36] = r_face[8]; // R[0] -> L[0]
                new_state[37] = r_face[7]; // R[1] -> L[1]
                new_state[38] = r_face[6]; // R[2] -> L[2]
                new_state[39] = r_face[5]; // R[3] -> L[3]
                new_state[40] = r_face[4]; // R[4] -> L[4]
                new_state[41] = r_face[3]; // R[5] -> L[5]
                new_state[42] = r_face[2]; // R[6] -> L[6]
                new_state[43] = r_face[1]; // R[7] -> L[7]
                new_state[44] = r_face[0]; // R[8] -> L[8]
                
                // F rotates 180°
                new_state[18] = f_face[8]; // F[0] <- F[8]
                new_state[19] = f_face[7]; // F[1] <- F[7]
                new_state[20] = f_face[6]; // F[2] <- F[6]
                new_state[21] = f_face[5]; // F[3] <- F[5]
                new_state[22] = f_face[4]; // F[4] <- F[4]
                new_state[23] = f_face[3]; // F[5] <- F[3]
                new_state[24] = f_face[2]; // F[6] <- F[2]
                new_state[25] = f_face[1]; // F[7] <- F[1]
                new_state[26] = f_face[0]; // F[8] <- F[0]
                
                // D -> U (with 180° rotation)
                new_state[0] = d_face[8];  // D[0] -> U[0]
                new_state[1] = d_face[7];  // D[1] -> U[1]
                new_state[2] = d_face[6];  // D[2] -> U[2]
                new_state[3] = d_face[5];  // D[3] -> U[3]
                new_state[4] = d_face[4];  // D[4] -> U[4]
                new_state[5] = d_face[3];  // D[5] -> U[5]
                new_state[6] = d_face[2];  // D[6] -> U[6]
                new_state[7] = d_face[1];  // D[7] -> U[7]
                new_state[8] = d_face[0];  // D[8] -> U[8]
                
                // L -> R (with 180° rotation)
                new_state[9] = l_face[8];  // L[0] -> R[0]
                new_state[10] = l_face[7]; // L[1] -> R[1]
                new_state[11] = l_face[6]; // L[2] -> R[2]
                new_state[12] = l_face[5]; // L[3] -> R[3]
                new_state[13] = l_face[4]; // L[4] -> R[4]
                new_state[14] = l_face[3]; // L[5] -> R[5]
                new_state[15] = l_face[2]; // L[6] -> R[6]
                new_state[16] = l_face[1]; // L[7] -> R[7]
                new_state[17] = l_face[0]; // L[8] -> R[8]
                
                // B rotates 180°
                new_state[45] = b_face[8]; // B[0] <- B[8]
                new_state[46] = b_face[7]; // B[1] <- B[7]
                new_state[47] = b_face[6]; // B[2] <- B[6]
                new_state[48] = b_face[5]; // B[3] <- B[5]
                new_state[49] = b_face[4]; // B[4] <- B[4]
                new_state[50] = b_face[3]; // B[5] <- B[3]
                new_state[51] = b_face[2]; // B[6] <- B[2]
                new_state[52] = b_face[1]; // B[7] <- B[1]
                new_state[53] = b_face[0]; // B[8] <- B[0]
            } else {
                // z' rotation: reverse of z  
                // Based on expected permutations: 0<-11, 1<-14, 2<-17, etc.
                
                // U <- R (with rotation)
                new_state[0] = r_face[2];  // R[2] -> U[0] (position 11 -> 0)
                new_state[1] = r_face[5];  // R[5] -> U[1] (position 14 -> 1)
                new_state[2] = r_face[8];  // R[8] -> U[2] (position 17 -> 2)
                new_state[3] = r_face[1];  // R[1] -> U[3] (position 10 -> 3)
                new_state[4] = r_face[4];  // R[4] -> U[4] (position 13 -> 4)
                new_state[5] = r_face[7];  // R[7] -> U[5] (position 16 -> 5)
                new_state[6] = r_face[0];  // R[0] -> U[6] (position 9 -> 6)
                new_state[7] = r_face[3];  // R[3] -> U[7] (position 12 -> 7)
                new_state[8] = r_face[6];  // R[6] -> U[8] (position 15 -> 8)
                
                // R <- D (with rotation) 
                new_state[9] = d_face[2];  // D[2] -> R[0] (position 29 -> 9)
                new_state[10] = d_face[5]; // D[5] -> R[1] (position 32 -> 10)
                new_state[11] = d_face[8]; // D[8] -> R[2] (position 35 -> 11)
                new_state[12] = d_face[1]; // D[1] -> R[3] (position 28 -> 12)
                new_state[13] = d_face[4]; // D[4] -> R[4] (position 31 -> 13)
                new_state[14] = d_face[7]; // D[7] -> R[5] (position 34 -> 14)
                new_state[15] = d_face[0]; // D[0] -> R[6] (position 27 -> 15)
                new_state[16] = d_face[3]; // D[3] -> R[7] (position 30 -> 16)
                new_state[17] = d_face[6]; // D[6] -> R[8] (position 33 -> 17)
                
                // F rotates counterclockwise
                new_state[18] = f_face[2]; // F[0] <- F[2]
                new_state[19] = f_face[5]; // F[1] <- F[5]
                new_state[20] = f_face[8]; // F[2] <- F[8]
                new_state[21] = f_face[1]; // F[3] <- F[1]
                new_state[22] = f_face[4]; // F[4] <- F[4]
                new_state[23] = f_face[7]; // F[5] <- F[7]
                new_state[24] = f_face[0]; // F[6] <- F[0]
                new_state[25] = f_face[3]; // F[7] <- F[3]
                new_state[26] = f_face[6]; // F[8] <- F[6]
                
                // D <- L (with rotation) - for z' (27<-38, 28<-41, 29<-44, etc.)
                new_state[27] = l_face[2]; // L[2] -> D[0] (position 38 -> 27)
                new_state[28] = l_face[5]; // L[5] -> D[1] (position 41 -> 28)
                new_state[29] = l_face[8]; // L[8] -> D[2] (position 44 -> 29)
                new_state[30] = l_face[1]; // L[1] -> D[3] (position 37 -> 30)
                new_state[31] = l_face[4]; // L[4] -> D[4] (position 40 -> 31)
                new_state[32] = l_face[7]; // L[7] -> D[5] (position 43 -> 32)
                new_state[33] = l_face[0]; // L[0] -> D[6] (position 36 -> 33)
                new_state[34] = l_face[3]; // L[3] -> D[7] (position 39 -> 34)
                new_state[35] = l_face[6]; // L[6] -> D[8] (position 42 -> 35)
                
                // L <- U (with rotation) - for z' (36<-2, 37<-5, 38<-8, etc.)
                new_state[36] = u_face[2]; // U[2] -> L[0] (position 2 -> 36)
                new_state[37] = u_face[5]; // U[5] -> L[1] (position 5 -> 37)
                new_state[38] = u_face[8]; // U[8] -> L[2] (position 8 -> 38)
                new_state[39] = u_face[1]; // U[1] -> L[3] (position 1 -> 39)
                new_state[40] = u_face[4]; // U[4] -> L[4] (position 4 -> 40)
                new_state[41] = u_face[7]; // U[7] -> L[5] (position 7 -> 41)
                new_state[42] = u_face[0]; // U[0] -> L[6] (position 0 -> 42)
                new_state[43] = u_face[3]; // U[3] -> L[7] (position 3 -> 43)
                new_state[44] = u_face[6]; // U[6] -> L[8] (position 6 -> 44)
                
                // B rotates clockwise
                new_state[45] = b_face[6]; // B[0] <- B[6]
                new_state[46] = b_face[3]; // B[1] <- B[3]
                new_state[47] = b_face[0]; // B[2] <- B[0]
                new_state[48] = b_face[7]; // B[3] <- B[7]
                new_state[49] = b_face[4]; // B[4] <- B[4]
                new_state[50] = b_face[1]; // B[5] <- B[1]
                new_state[51] = b_face[8]; // B[6] <- B[8]
                new_state[52] = b_face[5]; // B[7] <- B[5]
                new_state[53] = b_face[2]; // B[8] <- B[2]
            }
            break;
        }

        case 'u': {
            // u est équivalent à D y, optimisé en transformation directe
            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = new_state[j];
                r_face[j] = new_state[9 + j];
                f_face[j] = new_state[18 + j];
                d_face[j] = new_state[27 + j];
                l_face[j] = new_state[36 + j];
                b_face[j] = new_state[45 + j];
            }

            char u_rotated[9], d_rotated[9];

            if (direction == 1) {
                // u equivalent à D y - mais D ne doit PAS être modifiée selon notre analyse !
                rotate_face_clockwise(u_face, u_rotated);

                // Application des permutations correctes basées sur D y
                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];
                    // D face reste inchangée
                    new_state[27 + j] = d_face[j];
                }

                // Permutations spécifiques selon l'analyse
                new_state[ 9] = b_face[0]; // R[0]
                new_state[10] = b_face[1]; // R[1]
                new_state[11] = b_face[2]; // R[2]
                new_state[12] = b_face[3]; // R[3]
                new_state[13] = b_face[4]; // R[4]
                new_state[14] = b_face[5]; // R[5]
                new_state[18] = r_face[0]; // F[0]
                new_state[19] = r_face[1]; // F[1]
                new_state[20] = r_face[2]; // F[2]
                new_state[21] = r_face[3]; // F[3]
                new_state[22] = r_face[4]; // F[4]
                new_state[23] = r_face[5]; // F[5]
                new_state[36] = f_face[0]; // L[0]
                new_state[37] = f_face[1]; // L[1]
                new_state[38] = f_face[2]; // L[2]
                new_state[39] = f_face[3]; // L[3]
                new_state[40] = f_face[4]; // L[4]
                new_state[41] = f_face[5]; // L[5]
                new_state[45] = l_face[0]; // B[0]
                new_state[46] = l_face[1]; // B[1]
                new_state[47] = l_face[2]; // B[2]
                new_state[48] = l_face[3]; // B[3]
                new_state[49] = l_face[4]; // B[4]
                new_state[50] = l_face[5]; // B[5]

                // Bottom rows restent inchangées
                for (int j = 6; j < 9; j++) {
                    new_state[9 + j] = r_face[j];
                    new_state[18 + j] = f_face[j];
                    new_state[36 + j] = l_face[j];
                    new_state[45 + j] = b_face[j];
                }

            } else if (direction == 2) {
                // u2 equivalent à D2 y2 - mais D ne doit PAS être modifiée !
                rotate_face_180(u_face, u_rotated);

                // Application des permutations correctes
                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];
                    // D face reste inchangée
                    new_state[27 + j] = d_face[j];
                }

                // Permutations spécifiques pour u2 (effet y2)
                new_state[ 9] = l_face[0]; // R[0]
                new_state[10] = l_face[1]; // R[1]
                new_state[11] = l_face[2]; // R[2]
                new_state[12] = l_face[3]; // R[3]
                new_state[13] = l_face[4]; // R[4]
                new_state[14] = l_face[5]; // R[5]
                new_state[18] = b_face[0]; // F[0]
                new_state[19] = b_face[1]; // F[1]
                new_state[20] = b_face[2]; // F[2]
                new_state[21] = b_face[3]; // F[3]
                new_state[22] = b_face[4]; // F[4]
                new_state[23] = b_face[5]; // F[5]
                new_state[36] = r_face[0]; // L[0]
                new_state[37] = r_face[1]; // L[1]
                new_state[38] = r_face[2]; // L[2]
                new_state[39] = r_face[3]; // L[3]
                new_state[40] = r_face[4]; // L[4]
                new_state[41] = r_face[5]; // L[5]
                new_state[45] = f_face[0]; // B[0]
                new_state[46] = f_face[1]; // B[1]
                new_state[47] = f_face[2]; // B[2]
                new_state[48] = f_face[3]; // B[3]
                new_state[49] = f_face[4]; // B[4]
                new_state[50] = f_face[5]; // B[5]

                // Bottom rows restent inchangées
                for (int j = 6; j < 9; j++) {
                    new_state[9 + j] = r_face[j];
                    new_state[18 + j] = f_face[j];
                    new_state[36 + j] = l_face[j];
                    new_state[45 + j] = b_face[j];
                }
            } else {
                // u' equivalent à D' y' - mais D ne doit PAS être modifiée !
                rotate_face_counterclockwise(u_face, u_rotated);

                // Application des permutations correctes basées sur D' y'
                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];
                    // D face reste inchangée
                    new_state[27 + j] = d_face[j];
                }

                // Permutations spécifiques selon l'équivalence D' y'
                new_state[ 9] = f_face[0]; // R[0]
                new_state[10] = f_face[1]; // R[1]
                new_state[11] = f_face[2]; // R[2]
                new_state[12] = f_face[3]; // R[3]
                new_state[13] = f_face[4]; // R[4]
                new_state[14] = f_face[5]; // R[5]
                new_state[18] = l_face[0]; // F[0]
                new_state[19] = l_face[1]; // F[1]
                new_state[20] = l_face[2]; // F[2]
                new_state[21] = l_face[3]; // F[3]
                new_state[22] = l_face[4]; // F[4]
                new_state[23] = l_face[5]; // F[5]
                new_state[36] = b_face[0]; // L[0]
                new_state[37] = b_face[1]; // L[1]
                new_state[38] = b_face[2]; // L[2]
                new_state[39] = b_face[3]; // L[3]
                new_state[40] = b_face[4]; // L[4]
                new_state[41] = b_face[5]; // L[5]
                new_state[45] = r_face[0]; // B[0]
                new_state[46] = r_face[1]; // B[1]
                new_state[47] = r_face[2]; // B[2]
                new_state[48] = r_face[3]; // B[3]
                new_state[49] = r_face[4]; // B[4]
                new_state[50] = r_face[5]; // B[5]

                // Bottom rows restent inchangées
                for (int j = 6; j < 9; j++) {
                    new_state[9 + j] = r_face[j];
                    new_state[18 + j] = f_face[j];
                    new_state[36 + j] = l_face[j];
                    new_state[45 + j] = b_face[j];
                }
            }
            break;
        }

        case 'r': {
          // r est équivalent à L x, optimisé en transformation directe
          char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
          for (int j = 0; j < 9; j++) {
            u_face[j] = new_state[j];
            r_face[j] = new_state[9 + j];
            f_face[j] = new_state[18 + j];
            d_face[j] = new_state[27 + j];
            l_face[j] = new_state[36 + j];
            b_face[j] = new_state[45 + j];
          }

          char r_rotated[9], l_rotated[9];

          if (direction == 1) {
            // r : r = L x, corrections basées sur l'analyse des permutations
            rotate_face_clockwise(r_face, r_rotated);

            // Seule la face R tourne, L reste inchangée d'après l'analyse
            for (int j = 0; j < 9; j++) {
              new_state[9 + j] = r_rotated[j];
              new_state[36 + j] = l_face[j];  // L reste inchangée
            }

            // Corrections basées sur l'analyse - toutes les autres positions restent inchangées
            new_state[ 1] = f_face[1]; // U[1]
            new_state[ 2] = f_face[2]; // U[2]
            new_state[ 4] = f_face[4]; // U[4]
            new_state[ 5] = f_face[5]; // U[5]
            new_state[ 7] = f_face[7]; // U[7]
            new_state[ 8] = f_face[8]; // U[8]
            new_state[19] = d_face[1]; // F[1]
            new_state[20] = d_face[2]; // F[2]
            new_state[22] = d_face[4]; // F[4]
            new_state[23] = d_face[5]; // F[5]
            new_state[25] = d_face[7]; // F[7]
            new_state[26] = d_face[8]; // F[8]
            new_state[28] = b_face[7]; // D[1]
            new_state[29] = b_face[6]; // D[2]
            new_state[31] = b_face[4]; // D[4]
            new_state[32] = b_face[3]; // D[5]
            new_state[34] = b_face[1]; // D[7]
            new_state[35] = b_face[0]; // D[8]
            new_state[45] = u_face[8]; // B[0]
            new_state[46] = u_face[7]; // B[1]
            new_state[48] = u_face[5]; // B[3]
            new_state[49] = u_face[4]; // B[4]
            new_state[51] = u_face[2]; // B[6]
            new_state[52] = u_face[1]; // B[7]

            // Toutes les autres positions restent inchangées
            new_state[0] = u_face[0];
            new_state[3] = u_face[3];
            new_state[6] = u_face[6];
            new_state[18] = f_face[0];
            new_state[21] = f_face[3];
            new_state[24] = f_face[6];
            new_state[27] = d_face[0];
            new_state[30] = d_face[3];
            new_state[33] = d_face[6];
            new_state[47] = b_face[2];
            new_state[50] = b_face[5];
            new_state[53] = b_face[8];

          } else if (direction == 2) {
            // r2 = L2 x2, corrections basées sur l'analyse des permutations
            rotate_face_180(r_face, r_rotated);

            // Seule la face R tourne 180°, L reste inchangée d'après l'analyse
            for (int j = 0; j < 9; j++) {
              new_state[9 + j] = r_rotated[j];
              new_state[36 + j] = l_face[j];  // L reste inchangée
            }

            // Corrections exactes basées sur l'analyse L2 x2
            new_state[ 1] = d_face[1]; // U[1]
            new_state[ 2] = d_face[2]; // U[2]
            new_state[ 4] = d_face[4]; // U[4]
            new_state[ 5] = d_face[5]; // U[5]
            new_state[ 7] = d_face[7]; // U[7]
            new_state[ 8] = d_face[8]; // U[8]
            new_state[19] = b_face[7]; // F[1]
            new_state[20] = b_face[6]; // F[2]
            new_state[22] = b_face[4]; // F[4]
            new_state[23] = b_face[3]; // F[5]
            new_state[25] = b_face[1]; // F[7]
            new_state[26] = b_face[0]; // F[8]
            new_state[28] = u_face[1]; // D[1]
            new_state[29] = u_face[2]; // D[2]
            new_state[31] = u_face[4]; // D[4]
            new_state[32] = u_face[5]; // D[5]
            new_state[34] = u_face[7]; // D[7]
            new_state[35] = u_face[8]; // D[8]
            new_state[45] = f_face[8]; // B[0]
            new_state[46] = f_face[7]; // B[1]
            new_state[48] = f_face[5]; // B[3]
            new_state[49] = f_face[4]; // B[4]
            new_state[51] = f_face[2]; // B[6]
            new_state[52] = f_face[1]; // B[7]

            // Toutes les autres positions restent inchangées
            new_state[0] = u_face[0];
            new_state[3] = u_face[3];
            new_state[6] = u_face[6];
            new_state[18] = f_face[0];
            new_state[21] = f_face[3];
            new_state[24] = f_face[6];
            new_state[27] = d_face[0];
            new_state[30] = d_face[3];
            new_state[33] = d_face[6];
            new_state[47] = b_face[2];
            new_state[50] = b_face[5];
            new_state[53] = b_face[8];

          } else {
            // r' = L' x', corrections basées sur l'analyse des permutations
            rotate_face_counterclockwise(r_face, r_rotated);

            // Seule la face R tourne, L reste inchangée d'après l'analyse
            for (int j = 0; j < 9; j++) {
              new_state[9 + j] = r_rotated[j];
              new_state[36 + j] = l_face[j];  // L reste inchangée
            }

            // Corrections exactes basées sur l'analyse L' x'
            new_state[ 1] = b_face[7]; // U[1]
            new_state[ 2] = b_face[6]; // U[2]
            new_state[ 4] = b_face[4]; // U[4]
            new_state[ 5] = b_face[3]; // U[5]
            new_state[ 7] = b_face[1]; // U[7]
            new_state[ 8] = b_face[0]; // U[8]
            new_state[19] = u_face[1]; // F[1]
            new_state[20] = u_face[2]; // F[2]
            new_state[22] = u_face[4]; // F[4]
            new_state[23] = u_face[5]; // F[5]
            new_state[25] = u_face[7]; // F[7]
            new_state[26] = u_face[8]; // F[8]
            new_state[28] = f_face[1]; // D[1]
            new_state[29] = f_face[2]; // D[2]
            new_state[31] = f_face[4]; // D[4]
            new_state[32] = f_face[5]; // D[5]
            new_state[34] = f_face[7]; // D[7]
            new_state[35] = f_face[8]; // D[8]
            new_state[45] = d_face[8]; // B[0]
            new_state[46] = d_face[7]; // B[1]
            new_state[48] = d_face[5]; // B[3]
            new_state[49] = d_face[4]; // B[4]
            new_state[51] = d_face[2]; // B[6]
            new_state[52] = d_face[1]; // B[7]

            // Toutes les autres positions restent inchangées
            new_state[0] = u_face[0];
            new_state[3] = u_face[3];
            new_state[6] = u_face[6];
            new_state[18] = f_face[0];
            new_state[21] = f_face[3];
            new_state[24] = f_face[6];
            new_state[27] = d_face[0];
            new_state[30] = d_face[3];
            new_state[33] = d_face[6];
            new_state[47] = b_face[2];
            new_state[50] = b_face[5];
            new_state[53] = b_face[8];
          }
          break;
        }

        case 'f': {
            // Analyse directe des transformations f à partir des exemples donnés
            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = new_state[j];
                r_face[j] = new_state[9 + j];
                f_face[j] = new_state[18 + j];
                d_face[j] = new_state[27 + j];
                l_face[j] = new_state[36 + j];
                b_face[j] = new_state[45 + j];
            }

            char f_rotated[9];

            if (direction == 1) {
                // f equivalent à B z
                rotate_face_clockwise(f_face, f_rotated);

                // Application des permutations correctes basées sur B z
                new_state[ 3] = l_face[7]; // U[3]
                new_state[ 4] = l_face[4]; // U[4]
                new_state[ 5] = l_face[1]; // U[5]
                new_state[ 6] = l_face[8]; // U[6]
                new_state[ 7] = l_face[5]; // U[7]
                new_state[ 8] = l_face[2]; // U[8]
                new_state[ 9] = u_face[6]; // R[0]
                new_state[10] = u_face[3]; // R[1]
                new_state[12] = u_face[7]; // R[3]
                new_state[13] = u_face[4]; // R[4]
                new_state[15] = u_face[8]; // R[6]
                new_state[16] = u_face[5]; // R[7]
                new_state[18] = f_face[6]; // F[0]
                new_state[19] = f_face[3]; // F[1]
                new_state[20] = f_face[0]; // F[2]
                new_state[21] = f_face[7]; // F[3]
                new_state[22] = f_face[4]; // F[4] center
                new_state[23] = f_face[1]; // F[5]
                new_state[24] = f_face[8]; // F[6]
                new_state[25] = f_face[5]; // F[7]
                new_state[26] = f_face[2]; // F[8]
                new_state[27] = r_face[6]; // D[0]
                new_state[28] = r_face[3]; // D[1]
                new_state[29] = r_face[0]; // D[2]
                new_state[30] = r_face[7]; // D[3]
                new_state[31] = r_face[4]; // D[4]
                new_state[32] = r_face[1]; // D[5]
                new_state[37] = d_face[3]; // L[1]
                new_state[38] = d_face[0]; // L[2]
                new_state[40] = d_face[4]; // L[4]
                new_state[41] = d_face[1]; // L[5]
                new_state[43] = d_face[5]; // L[7]
                new_state[44] = d_face[2]; // L[8]

                // Elements non modifiés
                new_state[0] = u_face[0]; new_state[1] = u_face[1]; new_state[2] = u_face[2];
                new_state[11] = r_face[2]; new_state[14] = r_face[5]; new_state[17] = r_face[8];
                new_state[22] = f_rotated[4]; // F[4] center
                new_state[33] = d_face[6]; new_state[34] = d_face[7]; new_state[35] = d_face[8];
                new_state[36] = l_face[0]; new_state[39] = l_face[3]; new_state[42] = l_face[6];
                for (int j = 0; j < 9; j++) {
                    new_state[45 + j] = b_face[j];
                }

            } else if (direction == 2) {
                // f2 equivalent à B2 z2 - appliquer f deux fois
                rotate_face_180(f_face, f_rotated);
                
                // Application des corrections d'après l'analyse B2 z2
                new_state[ 3] = d_face[5]; // U[3]
                new_state[ 4] = d_face[4]; // U[4]
                new_state[ 5] = d_face[3]; // U[5]
                new_state[ 6] = d_face[2]; // U[6]
                new_state[ 7] = d_face[1]; // U[7]
                new_state[ 8] = d_face[0]; // U[8]
                new_state[ 9] = l_face[8]; // R[0]
                new_state[10] = l_face[7]; // R[1]
                new_state[12] = l_face[5]; // R[3]
                new_state[13] = l_face[4]; // R[4]
                new_state[15] = l_face[2]; // R[6]
                new_state[16] = l_face[1]; // R[7]
                new_state[18] = f_face[8]; // F[0]
                new_state[19] = f_face[7]; // F[1]
                new_state[20] = f_face[6]; // F[2]
                new_state[21] = f_face[5]; // F[3]
                new_state[23] = f_face[3]; // F[5]
                new_state[24] = f_face[2]; // F[6]
                new_state[25] = f_face[1]; // F[7]
                new_state[26] = f_face[0]; // F[8]
                new_state[27] = u_face[8]; // D[0]
                new_state[28] = u_face[7]; // D[1]
                new_state[29] = u_face[6]; // D[2]
                new_state[30] = u_face[5]; // D[3]
                new_state[31] = u_face[4]; // D[4]
                new_state[32] = u_face[3]; // D[5]
                new_state[37] = r_face[7]; // L[1]
                new_state[38] = r_face[6]; // L[2]
                new_state[40] = r_face[4]; // L[4]
                new_state[41] = r_face[3]; // L[5]
                new_state[43] = r_face[1]; // L[7]
                new_state[44] = r_face[0]; // L[8]

                // Éléments non modifiés
                new_state[0] = u_face[0]; new_state[1] = u_face[1]; new_state[2] = u_face[2];
                new_state[11] = r_face[2]; new_state[14] = r_face[5]; new_state[17] = r_face[8];
                new_state[22] = f_rotated[4]; // F[4] center
                new_state[33] = d_face[6]; new_state[34] = d_face[7]; new_state[35] = d_face[8];
                new_state[36] = l_face[0]; new_state[39] = l_face[3]; new_state[42] = l_face[6];
                for (int j = 0; j < 9; j++) {
                    new_state[45 + j] = b_face[j];
                }

            } else {
                // f' equivalent à B' z'
                rotate_face_counterclockwise(f_face, f_rotated);

                // Application des permutations correctes basées sur B' z'
                new_state[ 3] = r_face[1]; // U[3]
                new_state[ 4] = r_face[4]; // U[4]
                new_state[ 5] = r_face[7]; // U[5]
                new_state[ 6] = r_face[0]; // U[6]
                new_state[ 7] = r_face[3]; // U[7]
                new_state[ 8] = r_face[6]; // U[8]
                new_state[ 9] = d_face[2]; // R[0]
                new_state[10] = d_face[5]; // R[1]
                new_state[12] = d_face[1]; // R[3]
                new_state[13] = d_face[4]; // R[4]
                new_state[15] = d_face[0]; // R[6]
                new_state[16] = d_face[3]; // R[7]
                new_state[18] = f_face[2]; // F[0]
                new_state[19] = f_face[5]; // F[1]
                new_state[20] = f_face[8]; // F[2]
                new_state[21] = f_face[1]; // F[3]
                new_state[23] = f_face[7]; // F[5]
                new_state[24] = f_face[0]; // F[6]
                new_state[25] = f_face[3]; // F[7]
                new_state[26] = f_face[6]; // F[8]
                new_state[27] = l_face[2]; // D[0]
                new_state[28] = l_face[5]; // D[1]
                new_state[29] = l_face[8]; // D[2]
                new_state[30] = l_face[1]; // D[3]
                new_state[31] = l_face[4]; // D[4]
                new_state[32] = l_face[7]; // D[5]
                new_state[37] = u_face[5]; // L[1]
                new_state[38] = u_face[8]; // L[2]
                new_state[40] = u_face[4]; // L[4]
                new_state[41] = u_face[7]; // L[5]
                new_state[43] = u_face[3]; // L[7]
                new_state[44] = u_face[6]; // L[8]

                // Éléments non modifiés
                new_state[0] = u_face[0]; new_state[1] = u_face[1]; new_state[2] = u_face[2];
                new_state[11] = r_face[2]; new_state[14] = r_face[5]; new_state[17] = r_face[8];
                new_state[22] = f_rotated[4]; // F[4] center
                new_state[33] = d_face[6]; new_state[34] = d_face[7]; new_state[35] = d_face[8];
                new_state[36] = l_face[0]; new_state[39] = l_face[3]; new_state[42] = l_face[6];
                for (int j = 0; j < 9; j++) {
                    new_state[45 + j] = b_face[j];
                }
            }
            break;
        }

        case 'd': {
            // d est équivalent à U y'
            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = new_state[j];
                r_face[j] = new_state[9 + j];
                f_face[j] = new_state[18 + j];
                d_face[j] = new_state[27 + j];
                l_face[j] = new_state[36 + j];
                b_face[j] = new_state[45 + j];
            }

            char u_rotated[9], d_rotated[9];

            if (direction == 1) {
                // d equivalent à U y' - mais U ne doit PAS être modifiée selon l'analyse !
                rotate_face_clockwise(d_face, d_rotated);

                // Application des permutations correctes basées sur U y'
                for (int j = 0; j < 9; j++) {
                    // U face reste inchangée
                    new_state[j] = u_face[j];
                    new_state[27 + j] = d_rotated[j];
                }

                // Permutations spécifiques selon l'équivalence U y'
                new_state[12] = f_face[3]; // R[3]
                new_state[13] = f_face[4]; // R[4]
                new_state[14] = f_face[5]; // R[5]
                new_state[15] = f_face[6]; // R[6]
                new_state[16] = f_face[7]; // R[7]
                new_state[17] = f_face[8]; // R[8]
                new_state[21] = l_face[3]; // F[3]
                new_state[22] = l_face[4]; // F[4]
                new_state[23] = l_face[5]; // F[5]
                new_state[24] = l_face[6]; // F[6]
                new_state[25] = l_face[7]; // F[7]
                new_state[26] = l_face[8]; // F[8]
                new_state[39] = b_face[3]; // L[3]
                new_state[40] = b_face[4]; // L[4]
                new_state[41] = b_face[5]; // L[5]
                new_state[42] = b_face[6]; // L[6]
                new_state[43] = b_face[7]; // L[7]
                new_state[44] = b_face[8]; // L[8]
                new_state[48] = r_face[3]; // B[3]
                new_state[49] = r_face[4]; // B[4]
                new_state[50] = r_face[5]; // B[5]
                new_state[51] = r_face[6]; // B[6]
                new_state[52] = r_face[7]; // B[7]
                new_state[53] = r_face[8]; // B[8]

                // Top rows restent inchangées
                for (int j = 0; j < 3; j++) {
                    new_state[9 + j] = r_face[j];
                    new_state[18 + j] = f_face[j];
                    new_state[36 + j] = l_face[j];
                    new_state[45 + j] = b_face[j];
                }

            } else if (direction == 2) {
                // d2 equivalent à U2 y2 - mais U ne doit PAS être modifiée !
                rotate_face_180(d_face, d_rotated);

                // Application des permutations correctes
                for (int j = 0; j < 9; j++) {
                    // U face reste inchangée
                    new_state[j] = u_face[j];
                    new_state[27 + j] = d_rotated[j];
                }

                // Permutations spécifiques pour d2 (effet y2)
                new_state[12] = l_face[3]; // R[3]
                new_state[13] = l_face[4]; // R[4]
                new_state[14] = l_face[5]; // R[5]
                new_state[15] = l_face[6]; // R[6]
                new_state[16] = l_face[7]; // R[7]
                new_state[17] = l_face[8]; // R[8]
                new_state[21] = b_face[3]; // F[3]
                new_state[22] = b_face[4]; // F[4]
                new_state[23] = b_face[5]; // F[5]
                new_state[24] = b_face[6]; // F[6]
                new_state[25] = b_face[7]; // F[7]
                new_state[26] = b_face[8]; // F[8]
                new_state[39] = r_face[3]; // L[3]
                new_state[40] = r_face[4]; // L[4]
                new_state[41] = r_face[5]; // L[5]
                new_state[42] = r_face[6]; // L[6]
                new_state[43] = r_face[7]; // L[7]
                new_state[44] = r_face[8]; // L[8]
                new_state[48] = f_face[3]; // B[3]
                new_state[49] = f_face[4]; // B[4]
                new_state[50] = f_face[5]; // B[5]
                new_state[51] = f_face[6]; // B[6]
                new_state[52] = f_face[7]; // B[7]
                new_state[53] = f_face[8]; // B[8]

                // Top rows restent inchangées
                for (int j = 0; j < 3; j++) {
                    new_state[9 + j] = r_face[j];
                    new_state[18 + j] = f_face[j];
                    new_state[36 + j] = l_face[j];
                    new_state[45 + j] = b_face[j];
                }
            } else {
                // d' equivalent à U' y - mais U ne doit PAS être modifiée !
                rotate_face_counterclockwise(d_face, d_rotated);

                // Application des permutations correctes basées sur U' y
                for (int j = 0; j < 9; j++) {
                    // U face reste inchangée
                    new_state[j] = u_face[j];
                    new_state[27 + j] = d_rotated[j];
                }

                // Permutations spécifiques selon l'équivalence U' y
                new_state[12] = b_face[3]; // R[3]
                new_state[13] = b_face[4]; // R[4]
                new_state[14] = b_face[5]; // R[5]
                new_state[15] = b_face[6]; // R[6]
                new_state[16] = b_face[7]; // R[7]
                new_state[17] = b_face[8]; // R[8]
                new_state[21] = r_face[3]; // F[3]
                new_state[22] = r_face[4]; // F[4]
                new_state[23] = r_face[5]; // F[5]
                new_state[24] = r_face[6]; // F[6]
                new_state[25] = r_face[7]; // F[7]
                new_state[26] = r_face[8]; // F[8]
                new_state[39] = f_face[3]; // L[3]
                new_state[40] = f_face[4]; // L[4]
                new_state[41] = f_face[5]; // L[5]
                new_state[42] = f_face[6]; // L[6]
                new_state[43] = f_face[7]; // L[7]
                new_state[44] = f_face[8]; // L[8]
                new_state[48] = l_face[3]; // B[3]
                new_state[49] = l_face[4]; // B[4]
                new_state[50] = l_face[5]; // B[5]
                new_state[51] = l_face[6]; // B[6]
                new_state[52] = l_face[7]; // B[7]
                new_state[53] = l_face[8]; // B[8]

                // Top rows restent inchangées
                for (int j = 0; j < 3; j++) {
                    new_state[9 + j] = r_face[j];
                    new_state[18 + j] = f_face[j];
                    new_state[36 + j] = l_face[j];
                    new_state[45 + j] = b_face[j];
                }
            }
            break;
        }

        case 'l': {
            // l est équivalent à R x', optimisé en transformation directe
            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = new_state[j];
                r_face[j] = new_state[9 + j];
                f_face[j] = new_state[18 + j];
                d_face[j] = new_state[27 + j];
                l_face[j] = new_state[36 + j];
                b_face[j] = new_state[45 + j];
            }

            char l_rotated[9], r_rotated[9];

            if (direction == 1) {
                // l = R x', corrections basées sur l'analyse des permutations
                rotate_face_clockwise(l_face, l_rotated);

                // Seule la face L tourne, R reste inchangée d'après l'analyse
                for (int j = 0; j < 9; j++) {
                    new_state[36 + j] = l_rotated[j];
                    new_state[9 + j] = r_face[j];  // R reste inchangée
                }

                // Corrections exactes basées sur l'analyse
                new_state[ 0] = b_face[8]; // U[0]
                new_state[ 1] = b_face[7]; // U[1]
                new_state[ 3] = b_face[5]; // U[3]
                new_state[ 4] = b_face[4]; // U[4]
                new_state[ 6] = b_face[2]; // U[6]
                new_state[ 7] = b_face[1]; // U[7]
                new_state[18] = u_face[0]; // F[0]
                new_state[19] = u_face[1]; // F[1]
                new_state[21] = u_face[3]; // F[3]
                new_state[22] = u_face[4]; // F[4]
                new_state[24] = u_face[6]; // F[6]
                new_state[25] = u_face[7]; // F[7]
                new_state[27] = f_face[0]; // D[0]
                new_state[28] = f_face[1]; // D[1]
                new_state[30] = f_face[3]; // D[3]
                new_state[31] = f_face[4]; // D[4]
                new_state[33] = f_face[6]; // D[6]
                new_state[34] = f_face[7]; // D[7]
                new_state[46] = d_face[7]; // B[1]
                new_state[47] = d_face[6]; // B[2]
                new_state[49] = d_face[4]; // B[4]
                new_state[50] = d_face[3]; // B[5]
                new_state[52] = d_face[1]; // B[7]
                new_state[53] = d_face[0]; // B[8]

                // Toutes les autres positions restent inchangées
                new_state[2] = u_face[2];
                new_state[5] = u_face[5];
                new_state[8] = u_face[8];
                new_state[20] = f_face[2];
                new_state[23] = f_face[5];
                new_state[26] = f_face[8];
                new_state[29] = d_face[2];
                new_state[32] = d_face[5];
                new_state[35] = d_face[8];
                new_state[45] = b_face[0];
                new_state[48] = b_face[3];
                new_state[51] = b_face[6];

            } else if (direction == 2) {
                // l2 = R2 x2, corrections basées sur l'analyse des permutations
                rotate_face_180(l_face, l_rotated);

                // Seule la face L tourne 180°, R reste inchangée d'après l'analyse
                for (int j = 0; j < 9; j++) {
                    new_state[36 + j] = l_rotated[j];
                    new_state[9 + j] = r_face[j];  // R reste inchangée
                }

                // Corrections exactes basées sur l'analyse R2 x2
                new_state[ 0] = d_face[0]; // U[0]
                new_state[ 1] = d_face[1]; // U[1]
                new_state[ 3] = d_face[3]; // U[3]
                new_state[ 4] = d_face[4]; // U[4]
                new_state[ 6] = d_face[6]; // U[6]
                new_state[ 7] = d_face[7]; // U[7]
                new_state[18] = b_face[8]; // F[0]
                new_state[19] = b_face[7]; // F[1]
                new_state[21] = b_face[5]; // F[3]
                new_state[22] = b_face[4]; // F[4]
                new_state[24] = b_face[2]; // F[6]
                new_state[25] = b_face[1]; // F[7]
                new_state[27] = u_face[0]; // D[0]
                new_state[28] = u_face[1]; // D[1]
                new_state[30] = u_face[3]; // D[3]
                new_state[31] = u_face[4]; // D[4]
                new_state[33] = u_face[6]; // D[6]
                new_state[34] = u_face[7]; // D[7]
                new_state[46] = f_face[7]; // B[1]
                new_state[47] = f_face[6]; // B[2]
                new_state[49] = f_face[4]; // B[4]
                new_state[50] = f_face[3]; // B[5]
                new_state[52] = f_face[1]; // B[7]
                new_state[53] = f_face[0]; // B[8]

                // Toutes les autres positions restent inchangées
                new_state[2] = u_face[2];
                new_state[5] = u_face[5];
                new_state[8] = u_face[8];
                new_state[20] = f_face[2];
                new_state[23] = f_face[5];
                new_state[26] = f_face[8];
                new_state[29] = d_face[2];
                new_state[32] = d_face[5];
                new_state[35] = d_face[8];
                new_state[45] = b_face[0];
                new_state[48] = b_face[3];
                new_state[51] = b_face[6];

            } else {
                // l' = R' x, corrections basées sur l'analyse des permutations
                rotate_face_counterclockwise(l_face, l_rotated);

                // Seule la face L tourne, R reste inchangée d'après l'analyse
                for (int j = 0; j < 9; j++) {
                    new_state[36 + j] = l_rotated[j];
                    new_state[9 + j] = r_face[j];  // R reste inchangée
                }

                // Corrections exactes basées sur l'analyse R' x
                new_state[ 0] = f_face[0]; // U[0]
                new_state[ 1] = f_face[1]; // U[1]
                new_state[ 3] = f_face[3]; // U[3]
                new_state[ 4] = f_face[4]; // U[4]
                new_state[ 6] = f_face[6]; // U[6]
                new_state[ 7] = f_face[7]; // U[7]
                new_state[18] = d_face[0]; // F[0]
                new_state[19] = d_face[1]; // F[1]
                new_state[21] = d_face[3]; // F[3]
                new_state[22] = d_face[4]; // F[4]
                new_state[24] = d_face[6]; // F[6]
                new_state[25] = d_face[7]; // F[7]
                new_state[27] = b_face[8]; // D[0]
                new_state[28] = b_face[7]; // D[1]
                new_state[30] = b_face[5]; // D[3]
                new_state[31] = b_face[4]; // D[4]
                new_state[33] = b_face[2]; // D[6]
                new_state[34] = b_face[1]; // D[7]
                new_state[46] = u_face[7]; // B[1]
                new_state[47] = u_face[6]; // B[2]
                new_state[49] = u_face[4]; // B[4]
                new_state[50] = u_face[3]; // B[5]
                new_state[52] = u_face[1]; // B[7]
                new_state[53] = u_face[0]; // B[8]

                // Toutes les autres positions restent inchangées
                new_state[2] = u_face[2];
                new_state[5] = u_face[5];
                new_state[8] = u_face[8];
                new_state[20] = f_face[2];
                new_state[23] = f_face[5];
                new_state[26] = f_face[8];
                new_state[29] = d_face[2];
                new_state[32] = d_face[5];
                new_state[35] = d_face[8];
                new_state[45] = b_face[0];
                new_state[48] = b_face[3];
                new_state[51] = b_face[6];
            }
            break;
        }

        case 'b': {
            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = new_state[j];
                r_face[j] = new_state[9 + j];
                f_face[j] = new_state[18 + j];
                d_face[j] = new_state[27 + j];
                l_face[j] = new_state[36 + j];
                b_face[j] = new_state[45 + j];
            }

            if (direction == 1) {
              new_state[ 0] = r_face[2]; // U[0]
              new_state[ 1] = r_face[5]; // U[1]
              new_state[ 2] = r_face[8]; // U[2]
              new_state[ 3] = r_face[1]; // U[3]
              new_state[ 4] = r_face[4]; // U[4]
              new_state[ 5] = r_face[7]; // U[5]
              new_state[10] = d_face[5]; // R[1]
              new_state[11] = d_face[8]; // R[2]
              new_state[13] = d_face[4]; // R[4]
              new_state[14] = d_face[7]; // R[5]
              new_state[16] = d_face[3]; // R[7]
              new_state[17] = d_face[6]; // R[8]
              new_state[30] = l_face[1]; // D[3]
              new_state[31] = l_face[4]; // D[4]
              new_state[32] = l_face[7]; // D[5]
              new_state[33] = l_face[0]; // D[6]
              new_state[34] = l_face[3]; // D[7]
              new_state[35] = l_face[6]; // D[8]
              new_state[36] = u_face[2]; // L[0]
              new_state[37] = u_face[5]; // L[1]
              new_state[39] = u_face[1]; // L[3]
              new_state[40] = u_face[4]; // L[4]
              new_state[42] = u_face[0]; // L[6]
              new_state[43] = u_face[3]; // L[7]
              new_state[45] = b_face[6]; // B[0]
              new_state[46] = b_face[3]; // B[1]
              new_state[47] = b_face[0]; // B[2]
              new_state[48] = b_face[7]; // B[3]
              new_state[50] = b_face[1]; // B[5]
              new_state[51] = b_face[8]; // B[6]
              new_state[52] = b_face[5]; // B[7]
              new_state[53] = b_face[2]; // B[8]
            } else if (direction == 2) {
              new_state[ 0] = d_face[8]; // U[0]
              new_state[ 1] = d_face[7]; // U[1]
              new_state[ 2] = d_face[6]; // U[2]
              new_state[ 3] = d_face[5]; // U[3]
              new_state[ 4] = d_face[4]; // U[4]
              new_state[ 5] = d_face[3]; // U[5]
              new_state[10] = l_face[7]; // R[1]
              new_state[11] = l_face[6]; // R[2]
              new_state[13] = l_face[4]; // R[4]
              new_state[14] = l_face[3]; // R[5]
              new_state[16] = l_face[1]; // R[7]
              new_state[17] = l_face[0]; // R[8]
              new_state[30] = u_face[5]; // D[3]
              new_state[31] = u_face[4]; // D[4]
              new_state[32] = u_face[3]; // D[5]
              new_state[33] = u_face[2]; // D[6]
              new_state[34] = u_face[1]; // D[7]
              new_state[35] = u_face[0]; // D[8]
              new_state[36] = r_face[8]; // L[0]
              new_state[37] = r_face[7]; // L[1]
              new_state[39] = r_face[5]; // L[3]
              new_state[40] = r_face[4]; // L[4]
              new_state[42] = r_face[2]; // L[6]
              new_state[43] = r_face[1]; // L[7]
              new_state[45] = b_face[8]; // B[0]
              new_state[46] = b_face[7]; // B[1]
              new_state[47] = b_face[6]; // B[2]
              new_state[48] = b_face[5]; // B[3]
              new_state[50] = b_face[3]; // B[5]
              new_state[51] = b_face[2]; // B[6]
              new_state[52] = b_face[1]; // B[7]
              new_state[53] = b_face[0]; // B[8]
            } else {
              new_state[ 0] = l_face[6]; // U[0]
              new_state[ 1] = l_face[3]; // U[1]
              new_state[ 2] = l_face[0]; // U[2]
              new_state[ 3] = l_face[7]; // U[3]
              new_state[ 4] = l_face[4]; // U[4]
              new_state[ 5] = l_face[1]; // U[5]
              new_state[10] = u_face[3]; // R[1]
              new_state[11] = u_face[0]; // R[2]
              new_state[13] = u_face[4]; // R[4]
              new_state[14] = u_face[1]; // R[5]
              new_state[16] = u_face[5]; // R[7]
              new_state[17] = u_face[2]; // R[8]
              new_state[30] = r_face[7]; // D[3]
              new_state[31] = r_face[4]; // D[4]
              new_state[32] = r_face[1]; // D[5]
              new_state[33] = r_face[8]; // D[6]
              new_state[34] = r_face[5]; // D[7]
              new_state[35] = r_face[2]; // D[8]
              new_state[36] = d_face[6]; // L[0]
              new_state[37] = d_face[3]; // L[1]
              new_state[39] = d_face[7]; // L[3]
              new_state[40] = d_face[4]; // L[4]
              new_state[42] = d_face[8]; // L[6]
              new_state[43] = d_face[5]; // L[7]
              new_state[45] = b_face[2]; // B[0]
              new_state[46] = b_face[5]; // B[1]
              new_state[47] = b_face[8]; // B[2]
              new_state[48] = b_face[1]; // B[3]
              new_state[50] = b_face[7]; // B[5]
              new_state[51] = b_face[0]; // B[6]
              new_state[52] = b_face[3]; // B[7]
              new_state[53] = b_face[6]; // B[8]
            }
            break;
        }

        default:
            PyErr_Format(PyExc_ValueError, "Invalid move face: '%c'", face);
            return NULL;
    }

    return PyUnicode_FromString(new_state);
}

// Définition des méthodes du module
static PyMethodDef RotateMethods[] = {
    {"rotate_move", rotate_move, METH_VARARGS, "Rotate cube state with given move"},
    {NULL, NULL, 0, NULL}
};

// Définition du module
static struct PyModuleDef rotatemodule = {
    PyModuleDef_HEAD_INIT,
    "rotate",
    "Fast cube rotation operations",
    -1,
    RotateMethods
};

// Fonction d'initialisation du module
PyMODINIT_FUNC PyInit_rotate(void) {
    return PyModule_Create(&rotatemodule);
}
