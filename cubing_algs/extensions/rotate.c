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
            // x est la rotation de tout le cube autour de l'axe x (même que R)
            char temp_state[55];
            strcpy(temp_state, new_state);

            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = temp_state[j];
                r_face[j] = temp_state[9 + j];
                f_face[j] = temp_state[18 + j];
                d_face[j] = temp_state[27 + j];
                l_face[j] = temp_state[36 + j];
                b_face[j] = temp_state[45 + j];
            }

            char r_rotated[9], l_rotated[9];

            if (direction == 1) {
                rotate_face_clockwise(r_face, r_rotated);
                rotate_face_counterclockwise(l_face, l_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = f_face[j];        // U devient F
                    new_state[9 + j] = r_rotated[j]; // R reste R mais tourne
                    new_state[18 + j] = d_face[j];   // F devient D
                    new_state[27 + j] = b_face[8-j]; // D devient B inversé
                    new_state[36 + j] = l_rotated[j]; // L reste L mais tourne anti-horaire
                    new_state[45 + j] = u_face[8-j]; // B devient U inversé
                }
            } else if (direction == 2) {
                rotate_face_180(r_face, r_rotated);
                rotate_face_180(l_face, l_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = d_face[j];        // U devient D
                    new_state[9 + j] = r_rotated[j]; // R reste R mais tourne 180°
                    new_state[18 + j] = b_face[8-j]; // F devient B inversé
                    new_state[27 + j] = u_face[j];   // D devient U
                    new_state[36 + j] = l_rotated[j]; // L reste L mais tourne 180°
                    new_state[45 + j] = f_face[8-j]; // B devient F inversé
                }
            } else {
                rotate_face_counterclockwise(r_face, r_rotated);
                rotate_face_clockwise(l_face, l_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = b_face[8-j];      // U devient B inversé
                    new_state[9 + j] = r_rotated[j]; // R reste R mais tourne anti-horaire
                    new_state[18 + j] = u_face[j];   // F devient U
                    new_state[27 + j] = f_face[j];   // D devient F
                    new_state[36 + j] = l_rotated[j]; // L reste L mais tourne horaire
                    new_state[45 + j] = d_face[8-j]; // B devient D inversé
                }
            }
            break;
        }

        case 'y': {
            // y est la rotation de tout le cube autour de l'axe y (même que U)
            char temp_state[55];
            strcpy(temp_state, new_state);

            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = temp_state[j];
                r_face[j] = temp_state[9 + j];
                f_face[j] = temp_state[18 + j];
                d_face[j] = temp_state[27 + j];
                l_face[j] = temp_state[36 + j];
                b_face[j] = temp_state[45 + j];
            }

            char u_rotated[9], d_rotated[9];

            if (direction == 1) {
                rotate_face_clockwise(u_face, u_rotated);
                rotate_face_counterclockwise(d_face, d_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];     // U reste U mais tourne
                    new_state[9 + j] = b_face[j];    // R devient B
                    new_state[18 + j] = r_face[j];   // F devient R
                    new_state[27 + j] = d_rotated[j]; // D reste D mais tourne anti-horaire
                    new_state[36 + j] = f_face[j];   // L devient F
                    new_state[45 + j] = l_face[j];   // B devient L
                }
            } else if (direction == 2) {
                rotate_face_180(u_face, u_rotated);
                rotate_face_180(d_face, d_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];     // U reste U mais tourne 180°
                    new_state[9 + j] = l_face[j];    // R devient L
                    new_state[18 + j] = b_face[j];   // F devient B
                    new_state[27 + j] = d_rotated[j]; // D reste D mais tourne 180°
                    new_state[36 + j] = r_face[j];   // L devient R
                    new_state[45 + j] = f_face[j];   // B devient F
                }
            } else {
                rotate_face_counterclockwise(u_face, u_rotated);
                rotate_face_clockwise(d_face, d_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];     // U reste U mais tourne anti-horaire
                    new_state[9 + j] = f_face[j];    // R devient F
                    new_state[18 + j] = l_face[j];   // F devient L
                    new_state[27 + j] = d_rotated[j]; // D reste D mais tourne horaire
                    new_state[36 + j] = b_face[j];   // L devient B
                    new_state[45 + j] = r_face[j];   // B devient R
                }
            }
            break;
        }

        case 'z': {
            // z est la rotation de tout le cube autour de l'axe z (même que F)
            char temp_state[55];
            strcpy(temp_state, new_state);

            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = temp_state[j];
                r_face[j] = temp_state[9 + j];
                f_face[j] = temp_state[18 + j];
                d_face[j] = temp_state[27 + j];
                l_face[j] = temp_state[36 + j];
                b_face[j] = temp_state[45 + j];
            }

            char f_rotated[9], b_rotated[9];

            if (direction == 1) {
                rotate_face_clockwise(f_face, f_rotated);
                rotate_face_counterclockwise(b_face, b_rotated);

                // Transformation des autres faces (elles tournent en changeant de position)
                char u_transformed[9], r_transformed[9], d_transformed[9], l_transformed[9];
                for (int j = 0; j < 9; j++) {
                    u_transformed[j] = u_face[6 - 3*(j%3) + j/3];
                    r_transformed[j] = r_face[6 - 3*(j%3) + j/3];
                    d_transformed[j] = d_face[6 - 3*(j%3) + j/3];
                    l_transformed[j] = l_face[6 - 3*(j%3) + j/3];
                }

                for (int j = 0; j < 9; j++) {
                    new_state[j] = l_transformed[j];     // U devient L
                    new_state[9 + j] = u_transformed[j]; // R devient U
                    new_state[18 + j] = f_rotated[j];    // F reste F mais tourne
                    new_state[27 + j] = r_transformed[j]; // D devient R
                    new_state[36 + j] = d_transformed[j]; // L devient D
                    new_state[45 + j] = b_rotated[j];    // B reste B mais tourne anti-horaire
                }
            } else if (direction == 2) {
                rotate_face_180(f_face, f_rotated);
                rotate_face_180(b_face, b_rotated);

                // Transformation 180° des autres faces
                char u_transformed[9], r_transformed[9], d_transformed[9], l_transformed[9];
                for (int j = 0; j < 9; j++) {
                    u_transformed[j] = u_face[8-j];
                    r_transformed[j] = r_face[8-j];
                    d_transformed[j] = d_face[8-j];
                    l_transformed[j] = l_face[8-j];
                }

                for (int j = 0; j < 9; j++) {
                    new_state[j] = d_transformed[j];     // U devient D (inversé)
                    new_state[9 + j] = l_transformed[j]; // R devient L (inversé)
                    new_state[18 + j] = f_rotated[j];    // F reste F mais tourne 180°
                    new_state[27 + j] = u_transformed[j]; // D devient U (inversé)
                    new_state[36 + j] = r_transformed[j]; // L devient R (inversé)
                    new_state[45 + j] = b_rotated[j];    // B reste B mais tourne 180°
                }
            } else {
                rotate_face_counterclockwise(f_face, f_rotated);
                rotate_face_clockwise(b_face, b_rotated);

                // Transformation anti-horaire des autres faces
                char u_transformed[9], r_transformed[9], d_transformed[9], l_transformed[9];
                for (int j = 0; j < 9; j++) {
                    u_transformed[j] = u_face[2 + 3*(j%3) - j/3];
                    r_transformed[j] = r_face[2 + 3*(j%3) - j/3];
                    d_transformed[j] = d_face[2 + 3*(j%3) - j/3];
                    l_transformed[j] = l_face[2 + 3*(j%3) - j/3];
                }

                for (int j = 0; j < 9; j++) {
                    new_state[j] = r_transformed[j];     // U devient R
                    new_state[9 + j] = d_transformed[j]; // R devient D
                    new_state[18 + j] = f_rotated[j];    // F reste F mais tourne anti-horaire
                    new_state[27 + j] = l_transformed[j]; // D devient L
                    new_state[36 + j] = u_transformed[j]; // L devient U
                    new_state[45 + j] = b_rotated[j];    // B reste B mais tourne horaire
                }
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
                // u = D y : U horaire, D anti-horaire
                rotate_face_clockwise(u_face, u_rotated);
                rotate_face_counterclockwise(d_face, d_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];
                    new_state[27 + j] = d_rotated[j];
                }

                // Top et middle rows: seulement effet y (F->R, R->B, B->L, L->F)
                for (int j = 0; j < 6; j++) {
                    new_state[9 + j] = b_face[j];   // R <- B
                    new_state[18 + j] = r_face[j];  // F <- R
                    new_state[36 + j] = f_face[j];  // L <- F
                    new_state[45 + j] = l_face[j];  // B <- L
                }

                // Bottom rows: D et y s'annulent, restent identiques
                for (int j = 6; j < 9; j++) {
                    new_state[9 + j] = r_face[j];   // R bot unchanged
                    new_state[18 + j] = f_face[j];  // F bot unchanged
                    new_state[36 + j] = l_face[j];  // L bot unchanged
                    new_state[45 + j] = b_face[j];  // B bot unchanged
                }

            } else if (direction == 2) {
                // u2 = D2 y2
                rotate_face_180(u_face, u_rotated);
                rotate_face_180(d_face, d_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];
                    new_state[27 + j] = d_rotated[j];
                }

                // Top et middle rows: seulement y2 (F<->B, R<->L)
                for (int j = 0; j < 6; j++) {
                    new_state[9 + j] = l_face[j];      // R <- L
                    new_state[18 + j] = b_face[j];     // F <- B
                    new_state[36 + j] = r_face[j];     // L <- R
                    new_state[45 + j] = f_face[j];     // B <- F
                }

                // Bottom rows: D2 et y2 s'annulent, restent identiques
                for (int j = 6; j < 9; j++) {
                    new_state[9 + j] = r_face[j];      // R bot unchanged
                    new_state[18 + j] = f_face[j];     // F bot unchanged
                    new_state[36 + j] = l_face[j];     // L bot unchanged
                    new_state[45 + j] = b_face[j];     // B bot unchanged
                }
            } else {
                // u' = D' y'
                rotate_face_counterclockwise(u_face, u_rotated);
                rotate_face_clockwise(d_face, d_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];
                    new_state[27 + j] = d_rotated[j];
                }

                // Top et middle rows: effet y' (F->L, L->B, B->R, R->F)
                for (int j = 0; j < 6; j++) {
                    new_state[9 + j] = f_face[j];      // R <- F
                    new_state[18 + j] = l_face[j];     // F <- L
                    new_state[36 + j] = b_face[j];     // L <- B
                    new_state[45 + j] = r_face[j];     // B <- R
                }

                // Bottom rows: D' et y' s'annulent aussi
                for (int j = 6; j < 9; j++) {
                    new_state[9 + j] = r_face[j];      // R bot unchanged
                    new_state[18 + j] = f_face[j];     // F bot unchanged
                    new_state[36 + j] = l_face[j];     // L bot unchanged
                    new_state[45 + j] = b_face[j];     // B bot unchanged
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
            // r : analyse précise des transformations
            rotate_face_clockwise(r_face, r_rotated);
            rotate_face_counterclockwise(l_face, l_rotated);

            // Face R et L tournent
            for (int j = 0; j < 9; j++) {
              new_state[9 + j] = r_rotated[j];
              new_state[36 + j] = l_rotated[j];
            }

            // Transformation selon l'analyse position par position :
            // Position 0: U -> U (reste)
            new_state[0] = u_face[0];
            // Position 1: U -> F
            new_state[1] = f_face[1];
            // Position 2: U -> F
            new_state[2] = f_face[2];
            // Position 3: U -> U (reste)
            new_state[3] = u_face[3];
            // Position 4: U -> F
            new_state[4] = f_face[4];
            // Position 5: U -> F
            new_state[5] = f_face[5];
            // Position 6: U -> U (reste)
            new_state[6] = u_face[6];
            // Position 7: U -> F
            new_state[7] = f_face[7];
            // Position 8: U -> F
            new_state[8] = f_face[8];

            // Face F: positions 18-26
            // Position 18: F -> F (reste)
            new_state[18] = f_face[0];
            // Position 19: F -> D
            new_state[19] = d_face[1];
            // Position 20: F -> D
            new_state[20] = d_face[2];
            // Position 21: F -> F (reste)
            new_state[21] = f_face[3];
            // Position 22: F -> D
            new_state[22] = d_face[4];
            // Position 23: F -> D
            new_state[23] = d_face[5];
            // Position 24: F -> F (reste)
            new_state[24] = f_face[6];
            // Position 25: F -> D
            new_state[25] = d_face[7];
            // Position 26: F -> D
            new_state[26] = d_face[8];

            // Face D: positions 27-35
            // Position 27: D -> D (reste)
            new_state[27] = d_face[0];
            // Position 28: D -> B
            new_state[28] = b_face[7];
            // Position 29: D -> B
            new_state[29] = b_face[6];
            // Position 30: D -> D (reste)
            new_state[30] = d_face[3];
            // Position 31: D -> B
            new_state[31] = b_face[4];
            // Position 32: D -> B
            new_state[32] = b_face[3];
            // Position 33: D -> D (reste)
            new_state[33] = d_face[6];
            // Position 34: D -> B
            new_state[34] = b_face[1];
            // Position 35: D -> B
            new_state[35] = b_face[0];

            // Face B: positions 45-53
            // Position 45: B -> L (face L déjà appliquée dans l_rotated)
            new_state[45] = u_face[7];
            // Position 46: B -> U
            new_state[46] = u_face[8];
            // Position 47: B -> B (reste)
            new_state[47] = b_face[2];
            // Position 48: B -> U
            new_state[48] = u_face[4];
            // Position 49: B -> U
            new_state[49] = u_face[5];
            // Position 50: B -> B (reste)
            new_state[50] = b_face[5];
            // Position 51: B -> U
            new_state[51] = u_face[1];
            // Position 52: B -> U
            new_state[52] = u_face[2];
            // Position 53: B -> B (reste)
            new_state[53] = b_face[8];

          } else if (direction == 2) {
            // r2 : analyse précise position par position
            rotate_face_180(r_face, r_rotated);
            rotate_face_180(l_face, l_rotated);

            for (int j = 0; j < 9; j++) {
              new_state[9 + j] = r_rotated[j];
              new_state[36 + j] = l_rotated[j];
            }

            // Face U: UUUUUUUUU -> UDDUDDUD
            new_state[0] = u_face[0]; // U->U
            new_state[1] = d_face[1]; // U->D
            new_state[2] = d_face[2]; // U->D
            new_state[3] = u_face[3]; // U->U
            new_state[4] = d_face[4]; // U->D
            new_state[5] = d_face[5]; // U->D
            new_state[6] = u_face[6]; // U->U
            new_state[7] = d_face[7]; // U->D
            new_state[8] = d_face[8]; // U->D

            // Face F: FFFFFFFFF -> FBBFBBFBB
            new_state[18] = f_face[0]; // F->F
            new_state[19] = b_face[1]; // F->B
            new_state[20] = b_face[2]; // F->B
            new_state[21] = f_face[3]; // F->F
            new_state[22] = b_face[4]; // F->B
            new_state[23] = b_face[5]; // F->B
            new_state[24] = f_face[6]; // F->F
            new_state[25] = b_face[7]; // F->B
            new_state[26] = b_face[8]; // F->B

            // Face D: DDDDDDDDD -> DUUDUUDUU
            new_state[27] = d_face[0]; // D->D
            new_state[28] = u_face[1]; // D->U
            new_state[29] = u_face[2]; // D->U
            new_state[30] = d_face[3]; // D->D
            new_state[31] = u_face[4]; // D->U
            new_state[32] = u_face[5]; // D->U
            new_state[33] = d_face[6]; // D->D
            new_state[34] = u_face[7]; // D->U
            new_state[35] = u_face[8]; // D->U

            // Face B: BBBBBBBBB -> FFBFFBFFB
            new_state[45] = f_face[1]; // B->F
            new_state[46] = f_face[2]; // B->F
            new_state[47] = b_face[2]; // B->B
            new_state[48] = f_face[4]; // B->F
            new_state[49] = f_face[5]; // B->F
            new_state[50] = b_face[5]; // B->B
            new_state[51] = f_face[7]; // B->F
            new_state[52] = f_face[8]; // B->F
            new_state[53] = b_face[8]; // B->B

          } else {
            // r' : analyse précise position par position
            rotate_face_counterclockwise(r_face, r_rotated);
            rotate_face_clockwise(l_face, l_rotated);

            for (int j = 0; j < 9; j++) {
              new_state[9 + j] = r_rotated[j];
              new_state[36 + j] = l_rotated[j];
            }

            // Face U: UUUUUUUUU -> UBBUBBUB
            new_state[0] = u_face[0]; // U->U
            new_state[1] = b_face[1]; // U->B
            new_state[2] = b_face[2]; // U->B
            new_state[3] = u_face[3]; // U->U
            new_state[4] = b_face[4]; // U->B
            new_state[5] = b_face[5]; // U->B
            new_state[6] = u_face[6]; // U->U
            new_state[7] = b_face[7]; // U->B
            new_state[8] = b_face[8]; // U->B

            // Face F: FFFFFFFFF -> FUUFUUFUU
            new_state[18] = f_face[0]; // F->F
            new_state[19] = u_face[1]; // F->U
            new_state[20] = u_face[2]; // F->U
            new_state[21] = f_face[3]; // F->F
            new_state[22] = u_face[4]; // F->U
            new_state[23] = u_face[5]; // F->U
            new_state[24] = f_face[6]; // F->F
            new_state[25] = u_face[7]; // F->U
            new_state[26] = u_face[8]; // F->U

            // Face D: DDDDDDDDD -> DFFDFFDFF
            new_state[27] = d_face[0]; // D->D
            new_state[28] = f_face[1]; // D->F
            new_state[29] = f_face[2]; // D->F
            new_state[30] = d_face[3]; // D->D
            new_state[31] = f_face[4]; // D->F
            new_state[32] = f_face[5]; // D->F
            new_state[33] = d_face[6]; // D->D
            new_state[34] = f_face[7]; // D->F
            new_state[35] = f_face[8]; // D->F

            // Face B: BBBBBBBBB -> DDBDDBDDB
            new_state[45] = d_face[1]; // B->D
            new_state[46] = d_face[2]; // B->D
            new_state[47] = b_face[2]; // B->B
            new_state[48] = d_face[4]; // B->D
            new_state[49] = d_face[5]; // B->D
            new_state[50] = b_face[5]; // B->B
            new_state[51] = d_face[7]; // B->D
            new_state[52] = d_face[8]; // B->D
            new_state[53] = b_face[8]; // B->B
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
                // f: 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB' ->
                //    'UUULLLLLLUURUURUURFFFFFFFFFRRRRRRDDDLDDLDDLDDBBBBBBBBB'
                rotate_face_clockwise(f_face, f_rotated);

                // U face: UUU LLL LLL
                new_state[0] = u_face[0]; new_state[1] = u_face[1]; new_state[2] = u_face[2];
                new_state[3] = l_face[3]; new_state[4] = l_face[4]; new_state[5] = l_face[5];
                new_state[6] = l_face[6]; new_state[7] = l_face[7]; new_state[8] = l_face[8];

                // R face: UUR UUR UUR
                new_state[9] = u_face[3]; new_state[10] = u_face[4]; new_state[11] = r_face[2];
                new_state[12] = u_face[5]; new_state[13] = u_face[6]; new_state[14] = r_face[5];
                new_state[15] = u_face[7]; new_state[16] = u_face[8]; new_state[17] = r_face[8];

                // F face: rotated
                for (int j = 0; j < 9; j++) {
                    new_state[18 + j] = f_rotated[j];
                }

                // D face: RRR RRR DDD
                new_state[27] = r_face[0]; new_state[28] = r_face[1]; new_state[29] = r_face[3];
                new_state[30] = r_face[4]; new_state[31] = r_face[6]; new_state[32] = r_face[7];
                new_state[33] = d_face[6]; new_state[34] = d_face[7]; new_state[35] = d_face[8];

                // L face: LDD LDD LDD
                new_state[36] = l_face[0]; new_state[37] = d_face[0]; new_state[38] = d_face[3];
                new_state[39] = l_face[1]; new_state[40] = d_face[1]; new_state[41] = d_face[4];
                new_state[42] = l_face[2]; new_state[43] = d_face[2]; new_state[44] = d_face[5];

                // B face: unchanged
                for (int j = 0; j < 9; j++) {
                    new_state[45 + j] = b_face[j];
                }

            } else if (direction == 2) {
                // f2: 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB' ->
                //     'UUUDDDDDDLLRLLRLLRFFFFFFFFFUUUUUUDDDLRRLRRLRRBBBBBBBBB'
                rotate_face_180(f_face, f_rotated);

                // U face: UUU DDD DDD
                new_state[0] = u_face[0]; new_state[1] = u_face[1]; new_state[2] = u_face[2];
                new_state[3] = d_face[3]; new_state[4] = d_face[4]; new_state[5] = d_face[5];
                new_state[6] = d_face[6]; new_state[7] = d_face[7]; new_state[8] = d_face[8];

                // R face: LLR LLR LLR
                new_state[9] = l_face[0]; new_state[10] = l_face[1]; new_state[11] = r_face[2];
                new_state[12] = l_face[3]; new_state[13] = l_face[4]; new_state[14] = r_face[5];
                new_state[15] = l_face[6]; new_state[16] = l_face[7]; new_state[17] = r_face[8];

                // F face: rotated 180
                for (int j = 0; j < 9; j++) {
                    new_state[18 + j] = f_rotated[j];
                }

                // D face: UUU UUU DDD
                new_state[27] = u_face[6]; new_state[28] = u_face[7]; new_state[29] = u_face[8];
                new_state[30] = u_face[3]; new_state[31] = u_face[4]; new_state[32] = u_face[5];
                new_state[33] = d_face[6]; new_state[34] = d_face[7]; new_state[35] = d_face[8];

                // L face: LRR LRR LRR
                new_state[36] = l_face[8]; new_state[37] = r_face[0]; new_state[38] = r_face[1];
                new_state[39] = l_face[5]; new_state[40] = r_face[3]; new_state[41] = r_face[4];
                new_state[42] = l_face[2]; new_state[43] = r_face[6]; new_state[44] = r_face[7];

                // B face: unchanged
                for (int j = 0; j < 9; j++) {
                    new_state[45 + j] = b_face[j];
                }

            } else {
                // f': 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB' ->
                //     'UUURRRRRRDDRDDRDDRFFFFFFFFFLLLLLLDDDLUULUULUUBBBBBBBBB'
                rotate_face_counterclockwise(f_face, f_rotated);

                // U face: UUU RRR RRR
                new_state[0] = u_face[0]; new_state[1] = u_face[1]; new_state[2] = u_face[2];
                new_state[3] = r_face[3]; new_state[4] = r_face[4]; new_state[5] = r_face[5];
                new_state[6] = r_face[6]; new_state[7] = r_face[7]; new_state[8] = r_face[8];

                // R face: DDR DDR DDR
                new_state[9] = d_face[0]; new_state[10] = d_face[1]; new_state[11] = r_face[2];
                new_state[12] = d_face[3]; new_state[13] = d_face[4]; new_state[14] = r_face[5];
                new_state[15] = d_face[6]; new_state[16] = d_face[7]; new_state[17] = r_face[8];

                // F face: rotated counterclockwise
                for (int j = 0; j < 9; j++) {
                    new_state[18 + j] = f_rotated[j];
                }

                // D face: LLL LLL DDD
                new_state[27] = l_face[6]; new_state[28] = l_face[7]; new_state[29] = l_face[8];
                new_state[30] = l_face[3]; new_state[31] = l_face[4]; new_state[32] = l_face[5];
                new_state[33] = d_face[6]; new_state[34] = d_face[7]; new_state[35] = d_face[8];

                // L face: LUU LUU LUU
                new_state[36] = l_face[0]; new_state[37] = u_face[6]; new_state[38] = u_face[3];
                new_state[39] = l_face[1]; new_state[40] = u_face[7]; new_state[41] = u_face[4];
                new_state[42] = l_face[2]; new_state[43] = u_face[8]; new_state[44] = u_face[5];

                // B face: unchanged
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
                // d = U y' : U tourne anti-horaire, D tourne horaire
                rotate_face_counterclockwise(u_face, u_rotated);
                rotate_face_clockwise(d_face, d_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];
                    new_state[27 + j] = d_rotated[j];
                }

                // Bottom et middle rows: seulement effet y' (F->L, L->B, B->R, R->F)
                for (int j = 3; j < 9; j++) {
                    new_state[9 + j] = f_face[j];    // R <- F
                    new_state[18 + j] = l_face[j];   // F <- L
                    new_state[36 + j] = b_face[j];   // L <- B
                    new_state[45 + j] = r_face[j];   // B <- R
                }

                // Top rows: U et y' s'annulent, restent inchangées
                for (int j = 0; j < 3; j++) {
                    new_state[9 + j] = r_face[j];    // R top unchanged
                    new_state[18 + j] = f_face[j];   // F top unchanged
                    new_state[36 + j] = l_face[j];   // L top unchanged
                    new_state[45 + j] = b_face[j];   // B top unchanged
                }

            } else if (direction == 2) {
                // d2 = U2 y2
                rotate_face_180(u_face, u_rotated);
                rotate_face_180(d_face, d_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];
                    new_state[27 + j] = d_rotated[j];
                }

                // Bottom et middle rows: seulement y2 (F<->B, R<->L)
                for (int j = 3; j < 9; j++) {
                    new_state[9 + j] = l_face[j];      // R <- L
                    new_state[18 + j] = b_face[j];     // F <- B
                    new_state[36 + j] = r_face[j];     // L <- R
                    new_state[45 + j] = f_face[j];     // B <- F
                }

                // Top rows: U2 et y2 s'annulent, restent inchangées
                for (int j = 0; j < 3; j++) {
                    new_state[9 + j] = r_face[j];      // R top unchanged
                    new_state[18 + j] = f_face[j];     // F top unchanged
                    new_state[36 + j] = l_face[j];     // L top unchanged
                    new_state[45 + j] = b_face[j];     // B top unchanged
                }
            } else {
                // d' = U' y
                rotate_face_clockwise(u_face, u_rotated);
                rotate_face_counterclockwise(d_face, d_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[j] = u_rotated[j];
                    new_state[27 + j] = d_rotated[j];
                }

                // Bottom et middle rows: effet y (F->R, R->B, B->L, L->F)
                for (int j = 3; j < 9; j++) {
                    new_state[9 + j] = b_face[j];    // R <- B
                    new_state[18 + j] = r_face[j];   // F <- R
                    new_state[36 + j] = f_face[j];   // L <- F
                    new_state[45 + j] = l_face[j];   // B <- L
                }

                // Top rows: U' et y s'annulent, restent inchangées
                for (int j = 0; j < 3; j++) {
                    new_state[9 + j] = r_face[j];    // R top unchanged
                    new_state[18 + j] = f_face[j];   // F top unchanged
                    new_state[36 + j] = l_face[j];   // L top unchanged
                    new_state[45 + j] = b_face[j];   // B top unchanged
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
                // l = R x' : L horaire, R anti-horaire
                rotate_face_clockwise(l_face, l_rotated);
                rotate_face_counterclockwise(r_face, r_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[36 + j] = l_rotated[j];
                    new_state[9 + j] = r_rotated[j];
                }

                // Left et middle columns: seulement effet x' (U->B inv, B inv->D, D->F, F->U)
                for (int i = 0; i < 3; i++) {
                    new_state[i*3] = b_face[8 - i*3];      // U left <- B right inversé
                    new_state[18 + i*3] = u_face[i*3];     // F left <- U left
                    new_state[27 + i*3] = f_face[i*3];     // D left <- F left
                    new_state[45 + i*3 + 2] = d_face[i*3]; // B right <- D left
                }

                // Right columns: R et x' s'annulent, restent identiques
                for (int i = 0; i < 3; i++) {
                    new_state[i*3 + 2] = u_face[i*3 + 2]; // U right unchanged
                    new_state[18 + i*3 + 2] = f_face[i*3 + 2]; // F right unchanged
                    new_state[27 + i*3 + 2] = d_face[i*3 + 2]; // D right unchanged
                    new_state[45 + i*3] = b_face[i*3];         // B left unchanged
                }

                // Middle columns: seulement effet x'
                for (int i = 0; i < 3; i++) {
                    new_state[i*3 + 1] = b_face[8 - i*3 - 1];     // U middle <- B middle inversé
                    new_state[18 + i*3 + 1] = u_face[i*3 + 1];    // F middle <- U middle
                    new_state[27 + i*3 + 1] = f_face[i*3 + 1];    // D middle <- F middle
                    new_state[45 + i*3 + 1] = d_face[i*3 + 1];    // B middle <- D middle
                }

            } else if (direction == 2) {
                // l2 = R2 x2
                rotate_face_180(l_face, l_rotated);
                rotate_face_180(r_face, r_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[36 + j] = l_rotated[j];
                    new_state[9 + j] = r_rotated[j];
                }

                // Left et middle columns: seulement x2 (U<->D, F<->B inv)
                for (int i = 0; i < 3; i++) {
                    new_state[i*3] = d_face[i*3];              // U left <- D left
                    new_state[18 + i*3] = b_face[8 - i*3 - 2]; // F left <- B right inversé
                    new_state[27 + i*3] = u_face[i*3];         // D left <- U left
                    new_state[45 + i*3 + 2] = f_face[i*3];     // B right <- F left inversé
                }

                // Right columns: R2 et x2 s'annulent, restent identiques
                for (int i = 0; i < 3; i++) {
                    new_state[i*3 + 2] = u_face[i*3 + 2];     // U right unchanged
                    new_state[18 + i*3 + 2] = f_face[i*3 + 2]; // F right unchanged
                    new_state[27 + i*3 + 2] = d_face[i*3 + 2]; // D right unchanged
                    new_state[45 + i*3] = b_face[i*3];         // B left unchanged
                }

                // Middle columns: seulement x2
                for (int i = 0; i < 3; i++) {
                    new_state[i*3 + 1] = d_face[i*3 + 1];         // U middle <- D middle
                    new_state[18 + i*3 + 1] = b_face[8 - i*3 - 1]; // F middle <- B middle inversé
                    new_state[27 + i*3 + 1] = u_face[i*3 + 1];     // D middle <- U middle
                    new_state[45 + i*3 + 1] = f_face[i*3 + 1];     // B middle <- F middle inversé
                }

            } else {
                // l' = R' x
                rotate_face_counterclockwise(l_face, l_rotated);
                rotate_face_clockwise(r_face, r_rotated);

                for (int j = 0; j < 9; j++) {
                    new_state[36 + j] = l_rotated[j];
                    new_state[9 + j] = r_rotated[j];
                }

                // Left et middle columns: seulement effet x (U->F, F->D, D->B inv, B inv->U)
                for (int i = 0; i < 3; i++) {
                    new_state[i*3] = f_face[i*3];         // U left <- F left
                    new_state[18 + i*3] = d_face[i*3];    // F left <- D left
                    new_state[27 + i*3] = b_face[8 - i*3 - 2]; // D left <- B right inversé
                    new_state[45 + i*3 + 2] = u_face[i*3]; // B right <- U left
                }

                // Right columns: R' et x s'annulent aussi
                for (int i = 0; i < 3; i++) {
                    new_state[i*3 + 2] = u_face[i*3 + 2];     // U right unchanged
                    new_state[18 + i*3 + 2] = f_face[i*3 + 2]; // F right unchanged
                    new_state[27 + i*3 + 2] = d_face[i*3 + 2]; // D right unchanged
                    new_state[45 + i*3] = b_face[i*3];         // B left unchanged
                }

                // Middle columns: seulement effet x
                for (int i = 0; i < 3; i++) {
                    new_state[i*3 + 1] = f_face[i*3 + 1];     // U middle <- F middle
                    new_state[18 + i*3 + 1] = d_face[i*3 + 1]; // F middle <- D middle
                    new_state[27 + i*3 + 1] = b_face[8 - i*3 - 1]; // D middle <- B middle inversé
                    new_state[45 + i*3 + 1] = u_face[i*3 + 1]; // B middle <- U middle
                }
            }
            break;
        }

        case 'b': {
            // Analyse directe des transformations b à partir des exemples donnés
            char u_face[9], r_face[9], f_face[9], d_face[9], l_face[9], b_face[9];
            for (int j = 0; j < 9; j++) {
                u_face[j] = new_state[j];
                r_face[j] = new_state[9 + j];
                f_face[j] = new_state[18 + j];
                d_face[j] = new_state[27 + j];
                l_face[j] = new_state[36 + j];
                b_face[j] = new_state[45 + j];
            }

            char b_rotated[9];

            if (direction == 1) {
                // b: 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB' ->
                //    'RRRRRRUUURDDRDDRDDFFFFFFFFFDDDLLLLLLUULUULUULBBBBBBBBB'
                rotate_face_clockwise(b_face, b_rotated);

                // U face: RRR RRR UUU
                new_state[0] = r_face[0]; new_state[1] = r_face[1]; new_state[2] = r_face[2];
                new_state[3] = r_face[3]; new_state[4] = r_face[4]; new_state[5] = r_face[5];
                new_state[6] = u_face[6]; new_state[7] = u_face[7]; new_state[8] = u_face[8];

                // R face: RDD RDD RDD
                new_state[9] = r_face[6]; new_state[10] = d_face[0]; new_state[11] = d_face[3];
                new_state[12] = r_face[7]; new_state[13] = d_face[1]; new_state[14] = d_face[4];
                new_state[15] = r_face[8]; new_state[16] = d_face[2]; new_state[17] = d_face[5];

                // F face: unchanged
                for (int j = 0; j < 9; j++) {
                    new_state[18 + j] = f_face[j];
                }

                // D face: DDD LLL LLL
                new_state[27] = d_face[6]; new_state[28] = d_face[7]; new_state[29] = d_face[8];
                new_state[30] = l_face[0]; new_state[31] = l_face[1]; new_state[32] = l_face[2];
                new_state[33] = l_face[3]; new_state[34] = l_face[4]; new_state[35] = l_face[5];

                // L face: UUL UUL UUL
                new_state[36] = u_face[0]; new_state[37] = u_face[3]; new_state[38] = l_face[6];
                new_state[39] = u_face[1]; new_state[40] = u_face[4]; new_state[41] = l_face[7];
                new_state[42] = u_face[2]; new_state[43] = u_face[5]; new_state[44] = l_face[8];

                // B face: rotated
                for (int j = 0; j < 9; j++) {
                    new_state[45 + j] = b_rotated[j];
                }

            } else if (direction == 2) {
                // b2: 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB' ->
                //     'DDDDDDUUURLLRLLRLLFFFFFFFFFDDDUUUUUURRLRRLRRLBBBBBBBBB'
                rotate_face_180(b_face, b_rotated);

                // U face: DDD DDD UUU
                new_state[0] = d_face[0]; new_state[1] = d_face[1]; new_state[2] = d_face[2];
                new_state[3] = d_face[3]; new_state[4] = d_face[4]; new_state[5] = d_face[5];
                new_state[6] = u_face[6]; new_state[7] = u_face[7]; new_state[8] = u_face[8];

                // R face: RLL RLL RLL
                new_state[9] = r_face[6]; new_state[10] = l_face[0]; new_state[11] = l_face[3];
                new_state[12] = r_face[7]; new_state[13] = l_face[1]; new_state[14] = l_face[4];
                new_state[15] = r_face[8]; new_state[16] = l_face[2]; new_state[17] = l_face[5];

                // F face: unchanged
                for (int j = 0; j < 9; j++) {
                    new_state[18 + j] = f_face[j];
                }

                // D face: DDD UUU UUU
                new_state[27] = d_face[6]; new_state[28] = d_face[7]; new_state[29] = d_face[8];
                new_state[30] = u_face[0]; new_state[31] = u_face[1]; new_state[32] = u_face[2];
                new_state[33] = u_face[3]; new_state[34] = u_face[4]; new_state[35] = u_face[5];

                // L face: RRL RRL RRL
                new_state[36] = r_face[0]; new_state[37] = r_face[3]; new_state[38] = l_face[6];
                new_state[39] = r_face[1]; new_state[40] = r_face[4]; new_state[41] = l_face[7];
                new_state[42] = r_face[2]; new_state[43] = r_face[5]; new_state[44] = l_face[8];

                // B face: rotated 180
                for (int j = 0; j < 9; j++) {
                    new_state[45 + j] = b_rotated[j];
                }

            } else {
                // b': 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB' ->
                //     'LLLLLLUUURUURUURUUFFFFFFFFFDDDRRRRRRDDLDDLDDLBBBBBBBBB'
                rotate_face_counterclockwise(b_face, b_rotated);

                // U face: LLL LLL UUU
                new_state[0] = l_face[0]; new_state[1] = l_face[1]; new_state[2] = l_face[2];
                new_state[3] = l_face[3]; new_state[4] = l_face[4]; new_state[5] = l_face[5];
                new_state[6] = u_face[6]; new_state[7] = u_face[7]; new_state[8] = u_face[8];

                // R face: RUU RUU RUU
                new_state[9] = r_face[6]; new_state[10] = u_face[0]; new_state[11] = u_face[3];
                new_state[12] = r_face[7]; new_state[13] = u_face[1]; new_state[14] = u_face[4];
                new_state[15] = r_face[8]; new_state[16] = u_face[2]; new_state[17] = u_face[5];

                // F face: unchanged
                for (int j = 0; j < 9; j++) {
                    new_state[18 + j] = f_face[j];
                }

                // D face: DDD RRR RRR
                new_state[27] = d_face[6]; new_state[28] = d_face[7]; new_state[29] = d_face[8];
                new_state[30] = r_face[0]; new_state[31] = r_face[1]; new_state[32] = r_face[2];
                new_state[33] = r_face[3]; new_state[34] = r_face[4]; new_state[35] = r_face[5];

                // L face: DDL DDL DDL
                new_state[36] = d_face[0]; new_state[37] = d_face[3]; new_state[38] = l_face[6];
                new_state[39] = d_face[1]; new_state[40] = d_face[4]; new_state[41] = l_face[7];
                new_state[42] = d_face[2]; new_state[43] = d_face[5]; new_state[44] = l_face[8];

                // B face: rotated counterclockwise
                for (int j = 0; j < 9; j++) {
                    new_state[45 + j] = b_rotated[j];
                }
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
