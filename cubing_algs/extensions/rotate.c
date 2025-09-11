#include <Python.h>
#include <string.h>

// Main function for rotating a move
static PyObject* rotate_move(PyObject* self, PyObject* args) {
    const char* state;
    const char* move;

    if (!PyArg_ParseTuple(args, "ss", &state, &move)) {
        return NULL;
    }

    // Copy state for modification
    char new_state[55];
    strcpy(new_state, state);

    char temp_state[55];
    strcpy(temp_state, new_state);

    // Parse the move
    char face = move[0];
    int direction = 1; // Default: clockwise

    if (strlen(move) > 1) {
        if (move[1] == '\'') {
            direction = 3; // Anticlockwise
        } else if (move[1] == '2') {
            direction = 2; // 180°
        } else {
            PyErr_Format(PyExc_ValueError, "Invalid move modifier: '%c'", move[1]);
            return NULL;
        }
    }

    switch (face) {
        case 'U': {
            if (direction == 1) {
                // Face U rotation clockwise
                new_state[0] = temp_state[6];   // U[6] -> U[0]
                new_state[1] = temp_state[3];   // U[3] -> U[1]
                new_state[2] = temp_state[0];   // U[0] -> U[2]
                new_state[3] = temp_state[7];   // U[7] -> U[3]
                new_state[4] = temp_state[4];   // U[4] -> U[4]
                new_state[5] = temp_state[1];   // U[1] -> U[5]
                new_state[6] = temp_state[8];   // U[8] -> U[6]
                new_state[7] = temp_state[5];   // U[5] -> U[7]
                new_state[8] = temp_state[2];   // U[2] -> U[8]

                // Top row rotation (clockwise: R<-B, F<-R, L<-F, B<-L)
                new_state[9] = temp_state[45];   // B[0] -> R[0]
                new_state[10] = temp_state[46];  // B[1] -> R[1]
                new_state[11] = temp_state[47];  // B[2] -> R[2]
                new_state[18] = temp_state[9];   // R[0] -> F[0]
                new_state[19] = temp_state[10];  // R[1] -> F[1]
                new_state[20] = temp_state[11];  // R[2] -> F[2]
                new_state[36] = temp_state[18];  // F[0] -> L[0]
                new_state[37] = temp_state[19];  // F[1] -> L[1]
                new_state[38] = temp_state[20];  // F[2] -> L[2]
                new_state[45] = temp_state[36];  // L[0] -> B[0]
                new_state[46] = temp_state[37];  // L[1] -> B[1]
                new_state[47] = temp_state[38];  // L[2] -> B[2]
            } else if (direction == 2) {
                // Face U rotation 180°
                new_state[0] = temp_state[8];   // U[8] -> U[0]
                new_state[1] = temp_state[7];   // U[7] -> U[1]
                new_state[2] = temp_state[6];   // U[6] -> U[2]
                new_state[3] = temp_state[5];   // U[5] -> U[3]
                new_state[4] = temp_state[4];   // U[4] -> U[4]
                new_state[5] = temp_state[3];   // U[3] -> U[5]
                new_state[6] = temp_state[2];   // U[2] -> U[6]
                new_state[7] = temp_state[1];   // U[1] -> U[7]
                new_state[8] = temp_state[0];   // U[0] -> U[8]

                // 180° top row rotation (R<-L, F<-B, L<-R, B<-F)
                new_state[9] = temp_state[36];   // L[0] -> R[0]
                new_state[10] = temp_state[37];  // L[1] -> R[1]
                new_state[11] = temp_state[38];  // L[2] -> R[2]
                new_state[18] = temp_state[45];  // B[0] -> F[0]
                new_state[19] = temp_state[46];  // B[1] -> F[1]
                new_state[20] = temp_state[47];  // B[2] -> F[2]
                new_state[36] = temp_state[9];   // R[0] -> L[0]
                new_state[37] = temp_state[10];  // R[1] -> L[1]
                new_state[38] = temp_state[11];  // R[2] -> L[2]
                new_state[45] = temp_state[18];  // F[0] -> B[0]
                new_state[46] = temp_state[19];  // F[1] -> B[1]
                new_state[47] = temp_state[20];  // F[2] -> B[2]
            } else { // direction == 3 (counterclockwise)
                // Face U rotation counterclockwise
                new_state[0] = temp_state[2];   // U[2] -> U[0]
                new_state[1] = temp_state[5];   // U[5] -> U[1]
                new_state[2] = temp_state[8];   // U[8] -> U[2]
                new_state[3] = temp_state[1];   // U[1] -> U[3]
                new_state[4] = temp_state[4];   // U[4] -> U[4]
                new_state[5] = temp_state[7];   // U[7] -> U[5]
                new_state[6] = temp_state[0];   // U[0] -> U[6]
                new_state[7] = temp_state[3];   // U[3] -> U[7]
                new_state[8] = temp_state[6];   // U[6] -> U[8]

                // Top row rotation (counterclockwise: R<-F, F<-L, L<-B, B<-R)
                new_state[9] = temp_state[18];   // F[0] -> R[0]
                new_state[10] = temp_state[19];  // F[1] -> R[1]
                new_state[11] = temp_state[20];  // F[2] -> R[2]
                new_state[18] = temp_state[36];  // L[0] -> F[0]
                new_state[19] = temp_state[37];  // L[1] -> F[1]
                new_state[20] = temp_state[38];  // L[2] -> F[2]
                new_state[36] = temp_state[45];  // B[0] -> L[0]
                new_state[37] = temp_state[46];  // B[1] -> L[1]
                new_state[38] = temp_state[47];  // B[2] -> L[2]
                new_state[45] = temp_state[9];   // R[0] -> B[0]
                new_state[46] = temp_state[10];  // R[1] -> B[1]
                new_state[47] = temp_state[11];  // R[2] -> B[2]
            }
            break;
        }

        case 'R': {
            if (direction == 1) {
                // Face R rotation clockwise
                new_state[9] = temp_state[15];   // R[6] -> R[0]
                new_state[10] = temp_state[12];  // R[3] -> R[1]
                new_state[11] = temp_state[9];   // R[0] -> R[2]
                new_state[12] = temp_state[16];  // R[7] -> R[3]
                new_state[13] = temp_state[13];  // R[4] -> R[4]
                new_state[14] = temp_state[10];  // R[1] -> R[5]
                new_state[15] = temp_state[17];  // R[8] -> R[6]
                new_state[16] = temp_state[14];  // R[5] -> R[7]
                new_state[17] = temp_state[11];  // R[2] -> R[8]

                // Right column rotation (clockwise: U<-F, F<-D, D<-B, B<-U)
                new_state[2] = temp_state[20];   // F[2] -> U[2]
                new_state[5] = temp_state[23];   // F[5] -> U[5]
                new_state[8] = temp_state[26];   // F[8] -> U[8]
                new_state[20] = temp_state[29];  // D[2] -> F[2]
                new_state[23] = temp_state[32];  // D[5] -> F[5]
                new_state[26] = temp_state[35];  // D[8] -> F[8]
                new_state[29] = temp_state[51];  // B[6] -> D[2]
                new_state[32] = temp_state[48];  // B[3] -> D[5]
                new_state[35] = temp_state[45];  // B[0] -> D[8]
                new_state[45] = temp_state[8];   // U[8] -> B[0]
                new_state[48] = temp_state[5];   // U[5] -> B[3]
                new_state[51] = temp_state[2];   // U[2] -> B[6]
            } else if (direction == 2) {
                // Face R rotation 180°
                new_state[9] = temp_state[17];   // R[8] -> R[0]
                new_state[10] = temp_state[16];  // R[7] -> R[1]
                new_state[11] = temp_state[15];  // R[6] -> R[2]
                new_state[12] = temp_state[14];  // R[5] -> R[3]
                new_state[13] = temp_state[13];  // R[4] -> R[4]
                new_state[14] = temp_state[12];  // R[3] -> R[5]
                new_state[15] = temp_state[11];  // R[2] -> R[6]
                new_state[16] = temp_state[10];  // R[1] -> R[7]
                new_state[17] = temp_state[9];   // R[0] -> R[8]

                // 180° right column rotation (U<-D, F<-B, D<-U, B<-F)
                new_state[2] = temp_state[29];   // D[2] -> U[2]
                new_state[5] = temp_state[32];   // D[5] -> U[5]
                new_state[8] = temp_state[35];   // D[8] -> U[8]
                new_state[20] = temp_state[51];  // B[6] -> F[2]
                new_state[23] = temp_state[48];  // B[3] -> F[5]
                new_state[26] = temp_state[45];  // B[0] -> F[8]
                new_state[29] = temp_state[2];   // U[2] -> D[2]
                new_state[32] = temp_state[5];   // U[5] -> D[5]
                new_state[35] = temp_state[8];   // U[8] -> D[8]
                new_state[45] = temp_state[26];  // F[8] -> B[0]
                new_state[48] = temp_state[23];  // F[5] -> B[3]
                new_state[51] = temp_state[20];  // F[2] -> B[6]
            } else { // direction == 3 (counterclockwise)
                // Face R rotation counterclockwise
                new_state[9] = temp_state[11];   // R[2] -> R[0]
                new_state[10] = temp_state[14];  // R[5] -> R[1]
                new_state[11] = temp_state[17];  // R[8] -> R[2]
                new_state[12] = temp_state[10];  // R[1] -> R[3]
                new_state[13] = temp_state[13];  // R[4] -> R[4]
                new_state[14] = temp_state[16];  // R[7] -> R[5]
                new_state[15] = temp_state[9];   // R[0] -> R[6]
                new_state[16] = temp_state[12];  // R[3] -> R[7]
                new_state[17] = temp_state[15];  // R[6] -> R[8]

                // Right column rotation (counterclockwise: U<-B, F<-U, D<-F, B<-D)
                new_state[2] = temp_state[51];   // B[6] -> U[2]
                new_state[5] = temp_state[48];   // B[3] -> U[5]
                new_state[8] = temp_state[45];   // B[0] -> U[8]
                new_state[20] = temp_state[2];   // U[2] -> F[2]
                new_state[23] = temp_state[5];   // U[5] -> F[5]
                new_state[26] = temp_state[8];   // U[8] -> F[8]
                new_state[29] = temp_state[20];  // F[2] -> D[2]
                new_state[32] = temp_state[23];  // F[5] -> D[5]
                new_state[35] = temp_state[26];  // F[8] -> D[8]
                new_state[45] = temp_state[35];  // D[8] -> B[0]
                new_state[48] = temp_state[32];  // D[5] -> B[3]
                new_state[51] = temp_state[29];  // D[2] -> B[6]
            }
            break;
        }

        case 'F': {
            if (direction == 1) {
                // Face F rotation clockwise
                new_state[18] = temp_state[24];  // F[6] -> F[0]
                new_state[19] = temp_state[21];  // F[3] -> F[1]
                new_state[20] = temp_state[18];  // F[0] -> F[2]
                new_state[21] = temp_state[25];  // F[7] -> F[3]
                new_state[22] = temp_state[22];  // F[4] -> F[4]
                new_state[23] = temp_state[19];  // F[1] -> F[5]
                new_state[24] = temp_state[26];  // F[8] -> F[6]
                new_state[25] = temp_state[23];  // F[5] -> F[7]
                new_state[26] = temp_state[20];  // F[2] -> F[8]

                // Front edge rotation (clockwise: U<-L, R<-U, D<-R, L<-D)
                new_state[6] = temp_state[44];   // L[8] -> U[6]
                new_state[7] = temp_state[41];   // L[5] -> U[7]
                new_state[8] = temp_state[38];   // L[2] -> U[8]
                new_state[9] = temp_state[6];    // U[6] -> R[0]
                new_state[12] = temp_state[7];   // U[7] -> R[3]
                new_state[15] = temp_state[8];   // U[8] -> R[6]
                new_state[27] = temp_state[15];  // R[6] -> D[0]
                new_state[28] = temp_state[12];  // R[3] -> D[1]
                new_state[29] = temp_state[9];   // R[0] -> D[2]
                new_state[38] = temp_state[27];  // D[0] -> L[2]
                new_state[41] = temp_state[28];  // D[1] -> L[5]
                new_state[44] = temp_state[29];  // D[2] -> L[8]
            } else if (direction == 2) {
                // Face F rotation 180°
                new_state[18] = temp_state[26];  // F[8] -> F[0]
                new_state[19] = temp_state[25];  // F[7] -> F[1]
                new_state[20] = temp_state[24];  // F[6] -> F[2]
                new_state[21] = temp_state[23];  // F[5] -> F[3]
                new_state[22] = temp_state[22];  // F[4] -> F[4]
                new_state[23] = temp_state[21];  // F[3] -> F[5]
                new_state[24] = temp_state[20];  // F[2] -> F[6]
                new_state[25] = temp_state[19];  // F[1] -> F[7]
                new_state[26] = temp_state[18];  // F[0] -> F[8]

                // 180° front edge rotation (U<-D, R<-L, D<-U, L<-R)
                new_state[6] = temp_state[29];   // D[2] -> U[6]
                new_state[7] = temp_state[28];   // D[1] -> U[7]
                new_state[8] = temp_state[27];   // D[0] -> U[8]
                new_state[9] = temp_state[44];   // L[8] -> R[0]
                new_state[12] = temp_state[41];  // L[5] -> R[3]
                new_state[15] = temp_state[38];  // L[2] -> R[6]
                new_state[27] = temp_state[8];   // U[8] -> D[0]
                new_state[28] = temp_state[7];   // U[7] -> D[1]
                new_state[29] = temp_state[6];   // U[6] -> D[2]
                new_state[38] = temp_state[15];  // R[6] -> L[2]
                new_state[41] = temp_state[12];  // R[3] -> L[5]
                new_state[44] = temp_state[9];   // R[0] -> L[8]
            } else { // direction == 3 (counterclockwise)
                // Face F rotation counterclockwise
                new_state[18] = temp_state[20];  // F[2] -> F[0]
                new_state[19] = temp_state[23];  // F[5] -> F[1]
                new_state[20] = temp_state[26];  // F[8] -> F[2]
                new_state[21] = temp_state[19];  // F[1] -> F[3]
                new_state[22] = temp_state[22];  // F[4] -> F[4]
                new_state[23] = temp_state[25];  // F[7] -> F[5]
                new_state[24] = temp_state[18];  // F[0] -> F[6]
                new_state[25] = temp_state[21];  // F[3] -> F[7]
                new_state[26] = temp_state[24];  // F[6] -> F[8]

                // Front edge rotation (counterclockwise: U<-R, R<-D, D<-L, L<-U)
                new_state[6] = temp_state[9];    // R[0] -> U[6]
                new_state[7] = temp_state[12];   // R[3] -> U[7]
                new_state[8] = temp_state[15];   // R[6] -> U[8]
                new_state[9] = temp_state[29];   // D[2] -> R[0]
                new_state[12] = temp_state[28];  // D[1] -> R[3]
                new_state[15] = temp_state[27];  // D[0] -> R[6]
                new_state[27] = temp_state[38];  // L[2] -> D[0]
                new_state[28] = temp_state[41];  // L[5] -> D[1]
                new_state[29] = temp_state[44];  // L[8] -> D[2]
                new_state[38] = temp_state[8];   // U[8] -> L[2]
                new_state[41] = temp_state[7];   // U[7] -> L[5]
                new_state[44] = temp_state[6];   // U[6] -> L[8]
            }
            break;
        }

        case 'D': {
            if (direction == 1) {
                // Face D rotation clockwise
                new_state[27] = temp_state[33];  // D[6] -> D[0]
                new_state[28] = temp_state[30];  // D[3] -> D[1]
                new_state[29] = temp_state[27];  // D[0] -> D[2]
                new_state[30] = temp_state[34];  // D[7] -> D[3]
                new_state[31] = temp_state[31];  // D[4] -> D[4]
                new_state[32] = temp_state[28];  // D[1] -> D[5]
                new_state[33] = temp_state[35];  // D[8] -> D[6]
                new_state[34] = temp_state[32];  // D[5] -> D[7]
                new_state[35] = temp_state[29];  // D[2] -> D[8]

                // Bottom row rotation (clockwise: F<-L, R<-F, B<-R, L<-B)
                new_state[24] = temp_state[42];  // L[6] -> F[6]
                new_state[25] = temp_state[43];  // L[7] -> F[7]
                new_state[26] = temp_state[44];  // L[8] -> F[8]
                new_state[15] = temp_state[24];  // F[6] -> R[6]
                new_state[16] = temp_state[25];  // F[7] -> R[7]
                new_state[17] = temp_state[26];  // F[8] -> R[8]
                new_state[51] = temp_state[15];  // R[6] -> B[6]
                new_state[52] = temp_state[16];  // R[7] -> B[7]
                new_state[53] = temp_state[17];  // R[8] -> B[8]
                new_state[42] = temp_state[51];  // B[6] -> L[6]
                new_state[43] = temp_state[52];  // B[7] -> L[7]
                new_state[44] = temp_state[53];  // B[8] -> L[8]
            } else if (direction == 2) {
                // Face D rotation 180°
                new_state[27] = temp_state[35];  // D[8] -> D[0]
                new_state[28] = temp_state[34];  // D[7] -> D[1]
                new_state[29] = temp_state[33];  // D[6] -> D[2]
                new_state[30] = temp_state[32];  // D[5] -> D[3]
                new_state[31] = temp_state[31];  // D[4] -> D[4]
                new_state[32] = temp_state[30];  // D[3] -> D[5]
                new_state[33] = temp_state[29];  // D[2] -> D[6]
                new_state[34] = temp_state[28];  // D[1] -> D[7]
                new_state[35] = temp_state[27];  // D[0] -> D[8]

                // 180° bottom row rotation (F<-B, R<-L, B<-F, L<-R)
                new_state[24] = temp_state[51];  // B[6] -> F[6]
                new_state[25] = temp_state[52];  // B[7] -> F[7]
                new_state[26] = temp_state[53];  // B[8] -> F[8]
                new_state[15] = temp_state[42];  // L[6] -> R[6]
                new_state[16] = temp_state[43];  // L[7] -> R[7]
                new_state[17] = temp_state[44];  // L[8] -> R[8]
                new_state[51] = temp_state[24];  // F[6] -> B[6]
                new_state[52] = temp_state[25];  // F[7] -> B[7]
                new_state[53] = temp_state[26];  // F[8] -> B[8]
                new_state[42] = temp_state[15];  // R[6] -> L[6]
                new_state[43] = temp_state[16];  // R[7] -> L[7]
                new_state[44] = temp_state[17];  // R[8] -> L[8]
            } else { // direction == 3 (counterclockwise)
                // Face D rotation counterclockwise
                new_state[27] = temp_state[29];  // D[2] -> D[0]
                new_state[28] = temp_state[32];  // D[5] -> D[1]
                new_state[29] = temp_state[35];  // D[8] -> D[2]
                new_state[30] = temp_state[28];  // D[1] -> D[3]
                new_state[31] = temp_state[31];  // D[4] -> D[4]
                new_state[32] = temp_state[34];  // D[7] -> D[5]
                new_state[33] = temp_state[27];  // D[0] -> D[6]
                new_state[34] = temp_state[30];  // D[3] -> D[7]
                new_state[35] = temp_state[33];  // D[6] -> D[8]

                // Bottom row rotation (counterclockwise: F<-R, R<-B, B<-L, L<-F)
                new_state[24] = temp_state[15];  // R[6] -> F[6]
                new_state[25] = temp_state[16];  // R[7] -> F[7]
                new_state[26] = temp_state[17];  // R[8] -> F[8]
                new_state[15] = temp_state[51];  // B[6] -> R[6]
                new_state[16] = temp_state[52];  // B[7] -> R[7]
                new_state[17] = temp_state[53];  // B[8] -> R[8]
                new_state[51] = temp_state[42];  // L[6] -> B[6]
                new_state[52] = temp_state[43];  // L[7] -> B[7]
                new_state[53] = temp_state[44];  // L[8] -> B[8]
                new_state[42] = temp_state[24];  // F[6] -> L[6]
                new_state[43] = temp_state[25];  // F[7] -> L[7]
                new_state[44] = temp_state[26];  // F[8] -> L[8]
            }
            break;
        }

        case 'L': {
            if (direction == 1) {
                // Face L rotation clockwise
                new_state[36] = temp_state[42];  // L[6] -> L[0]
                new_state[37] = temp_state[39];  // L[3] -> L[1]
                new_state[38] = temp_state[36];  // L[0] -> L[2]
                new_state[39] = temp_state[43];  // L[7] -> L[3]
                new_state[40] = temp_state[40];  // L[4] -> L[4]
                new_state[41] = temp_state[37];  // L[1] -> L[5]
                new_state[42] = temp_state[44];  // L[8] -> L[6]
                new_state[43] = temp_state[41];  // L[5] -> L[7]
                new_state[44] = temp_state[38];  // L[2] -> L[8]

                // Left column rotation (clockwise: U<-B, F<-U, D<-F, B<-D)
                new_state[0] = temp_state[53];   // B[8] -> U[0]
                new_state[3] = temp_state[50];   // B[5] -> U[3]
                new_state[6] = temp_state[47];   // B[2] -> U[6]
                new_state[18] = temp_state[0];   // U[0] -> F[0]
                new_state[21] = temp_state[3];   // U[3] -> F[3]
                new_state[24] = temp_state[6];   // U[6] -> F[6]
                new_state[27] = temp_state[18];  // F[0] -> D[0]
                new_state[30] = temp_state[21];  // F[3] -> D[3]
                new_state[33] = temp_state[24];  // F[6] -> D[6]
                new_state[47] = temp_state[33];  // D[6] -> B[2]
                new_state[50] = temp_state[30];  // D[3] -> B[5]
                new_state[53] = temp_state[27];  // D[0] -> B[8]
            } else if (direction == 2) {
                // Face L rotation 180°
                new_state[36] = temp_state[44];  // L[8] -> L[0]
                new_state[37] = temp_state[43];  // L[7] -> L[1]
                new_state[38] = temp_state[42];  // L[6] -> L[2]
                new_state[39] = temp_state[41];  // L[5] -> L[3]
                new_state[40] = temp_state[40];  // L[4] -> L[4]
                new_state[41] = temp_state[39];  // L[3] -> L[5]
                new_state[42] = temp_state[38];  // L[2] -> L[6]
                new_state[43] = temp_state[37];  // L[1] -> L[7]
                new_state[44] = temp_state[36];  // L[0] -> L[8]

                // 180° left column rotation (U<-D, F<-B, D<-U, B<-F)
                new_state[0] = temp_state[27];   // D[0] -> U[0]
                new_state[3] = temp_state[30];   // D[3] -> U[3]
                new_state[6] = temp_state[33];   // D[6] -> U[6]
                new_state[18] = temp_state[53];  // B[8] -> F[0]
                new_state[21] = temp_state[50];  // B[5] -> F[3]
                new_state[24] = temp_state[47];  // B[2] -> F[6]
                new_state[27] = temp_state[0];   // U[0] -> D[0]
                new_state[30] = temp_state[3];   // U[3] -> D[3]
                new_state[33] = temp_state[6];   // U[6] -> D[6]
                new_state[47] = temp_state[24];  // F[6] -> B[2]
                new_state[50] = temp_state[21];  // F[3] -> B[5]
                new_state[53] = temp_state[18];  // F[0] -> B[8]
            } else { // direction == 3 (counterclockwise)
                // Face L rotation counterclockwise
                new_state[36] = temp_state[38];  // L[2] -> L[0]
                new_state[37] = temp_state[41];  // L[5] -> L[1]
                new_state[38] = temp_state[44];  // L[8] -> L[2]
                new_state[39] = temp_state[37];  // L[1] -> L[3]
                new_state[40] = temp_state[40];  // L[4] -> L[4]
                new_state[41] = temp_state[43];  // L[7] -> L[5]
                new_state[42] = temp_state[36];  // L[0] -> L[6]
                new_state[43] = temp_state[39];  // L[3] -> L[7]
                new_state[44] = temp_state[42];  // L[6] -> L[8]

                // Left column rotation (counterclockwise: U<-F, F<-D, D<-B, B<-U)
                new_state[0] = temp_state[18];   // F[0] -> U[0]
                new_state[3] = temp_state[21];   // F[3] -> U[3]
                new_state[6] = temp_state[24];   // F[6] -> U[6]
                new_state[18] = temp_state[27];  // D[0] -> F[0]
                new_state[21] = temp_state[30];  // D[3] -> F[3]
                new_state[24] = temp_state[33];  // D[6] -> F[6]
                new_state[27] = temp_state[53];  // B[8] -> D[0]
                new_state[30] = temp_state[50];  // B[5] -> D[3]
                new_state[33] = temp_state[47];  // B[2] -> D[6]
                new_state[47] = temp_state[6];   // U[6] -> B[2]
                new_state[50] = temp_state[3];   // U[3] -> B[5]
                new_state[53] = temp_state[0];   // U[0] -> B[8]
            }
            break;
        }

        case 'B': {
            if (direction == 1) {
                // Face B rotation clockwise
                new_state[45] = temp_state[51];  // B[6] -> B[0]
                new_state[46] = temp_state[48];  // B[3] -> B[1]
                new_state[47] = temp_state[45];  // B[0] -> B[2]
                new_state[48] = temp_state[52];  // B[7] -> B[3]
                new_state[49] = temp_state[49];  // B[4] -> B[4]
                new_state[50] = temp_state[46];  // B[1] -> B[5]
                new_state[51] = temp_state[53];  // B[8] -> B[6]
                new_state[52] = temp_state[50];  // B[5] -> B[7]
                new_state[53] = temp_state[47];  // B[2] -> B[8]

                // Back edge rotation (clockwise: U<-R, R<-D, D<-L, L<-U)
                new_state[0] = temp_state[11];   // R[2] -> U[0]
                new_state[1] = temp_state[14];   // R[5] -> U[1]
                new_state[2] = temp_state[17];   // R[8] -> U[2]
                new_state[11] = temp_state[35];  // D[8] -> R[2]
                new_state[14] = temp_state[34];  // D[7] -> R[5]
                new_state[17] = temp_state[33];  // D[6] -> R[8]
                new_state[33] = temp_state[36];  // L[0] -> D[6]
                new_state[34] = temp_state[39];  // L[3] -> D[7]
                new_state[35] = temp_state[42];  // L[6] -> D[8]
                new_state[36] = temp_state[2];   // U[2] -> L[0]
                new_state[39] = temp_state[1];   // U[1] -> L[3]
                new_state[42] = temp_state[0];   // U[0] -> L[6]
            } else if (direction == 2) {
                // Face B rotation 180°
                new_state[45] = temp_state[53];  // B[8] -> B[0]
                new_state[46] = temp_state[52];  // B[7] -> B[1]
                new_state[47] = temp_state[51];  // B[6] -> B[2]
                new_state[48] = temp_state[50];  // B[5] -> B[3]
                new_state[49] = temp_state[49];  // B[4] -> B[4]
                new_state[50] = temp_state[48];  // B[3] -> B[5]
                new_state[51] = temp_state[47];  // B[2] -> B[6]
                new_state[52] = temp_state[46];  // B[1] -> B[7]
                new_state[53] = temp_state[45];  // B[0] -> B[8]

                // 180° back edge rotation (U<-D, R<-L, D<-U, L<-R)
                new_state[0] = temp_state[35];   // D[8] -> U[0]
                new_state[1] = temp_state[34];   // D[7] -> U[1]
                new_state[2] = temp_state[33];   // D[6] -> U[2]
                new_state[11] = temp_state[42];  // L[6] -> R[2]
                new_state[14] = temp_state[39];  // L[3] -> R[5]
                new_state[17] = temp_state[36];  // L[0] -> R[8]
                new_state[33] = temp_state[2];   // U[2] -> D[6]
                new_state[34] = temp_state[1];   // U[1] -> D[7]
                new_state[35] = temp_state[0];   // U[0] -> D[8]
                new_state[36] = temp_state[17];  // R[8] -> L[0]
                new_state[39] = temp_state[14];  // R[5] -> L[3]
                new_state[42] = temp_state[11];  // R[2] -> L[6]
            } else { // direction == 3 (counterclockwise)
                // Face B rotation counterclockwise
                new_state[45] = temp_state[47];  // B[2] -> B[0]
                new_state[46] = temp_state[50];  // B[5] -> B[1]
                new_state[47] = temp_state[53];  // B[8] -> B[2]
                new_state[48] = temp_state[46];  // B[1] -> B[3]
                new_state[49] = temp_state[49];  // B[4] -> B[4]
                new_state[50] = temp_state[52];  // B[7] -> B[5]
                new_state[51] = temp_state[45];  // B[0] -> B[6]
                new_state[52] = temp_state[48];  // B[3] -> B[7]
                new_state[53] = temp_state[51];  // B[6] -> B[8]

                // Back edge rotation (counterclockwise: U<-L, R<-U, D<-R, L<-D)
                new_state[0] = temp_state[42];   // L[6] -> U[0]
                new_state[1] = temp_state[39];   // L[3] -> U[1]
                new_state[2] = temp_state[36];   // L[0] -> U[2]
                new_state[11] = temp_state[0];   // U[0] -> R[2]
                new_state[14] = temp_state[1];   // U[1] -> R[5]
                new_state[17] = temp_state[2];   // U[2] -> R[8]
                new_state[33] = temp_state[17];  // R[8] -> D[6]
                new_state[34] = temp_state[14];  // R[5] -> D[7]
                new_state[35] = temp_state[11];  // R[2] -> D[8]
                new_state[36] = temp_state[33];  // D[6] -> L[0]
                new_state[39] = temp_state[34];  // D[7] -> L[3]
                new_state[42] = temp_state[35];  // D[8] -> L[6]
            }
            break;
        }

        case 'M': {
            if (direction == 1) {
                // M rotation clockwise (same direction as L)
                new_state[1] = temp_state[52];   // B[7] -> U[1]
                new_state[4] = temp_state[49];   // B[4] -> U[4]
                new_state[7] = temp_state[46];   // B[1] -> U[7]
                new_state[19] = temp_state[1];   // U[1] -> F[1]
                new_state[22] = temp_state[4];   // U[4] -> F[4]
                new_state[25] = temp_state[7];   // U[7] -> F[7]
                new_state[28] = temp_state[19];  // F[1] -> D[1]
                new_state[31] = temp_state[22];  // F[4] -> D[4]
                new_state[34] = temp_state[25];  // F[7] -> D[7]
                new_state[46] = temp_state[34];  // D[7] -> B[1]
                new_state[49] = temp_state[31];  // D[4] -> B[4]
                new_state[52] = temp_state[28];  // D[1] -> B[7]
            } else if (direction == 2) {
                // M rotation 180°
                new_state[1] = temp_state[28];   // D[1] -> U[1]
                new_state[4] = temp_state[31];   // D[4] -> U[4]
                new_state[7] = temp_state[34];   // D[7] -> U[7]
                new_state[19] = temp_state[52];  // B[7] -> F[1]
                new_state[22] = temp_state[49];  // B[4] -> F[4]
                new_state[25] = temp_state[46];  // B[1] -> F[7]
                new_state[28] = temp_state[1];   // U[1] -> D[1]
                new_state[31] = temp_state[4];   // U[4] -> D[4]
                new_state[34] = temp_state[7];   // U[7] -> D[7]
                new_state[46] = temp_state[25];  // F[7] -> B[1]
                new_state[49] = temp_state[22];  // F[4] -> B[4]
                new_state[52] = temp_state[19];  // F[1] -> B[7]
            } else { // direction == 3 (counterclockwise)
                // M rotation counterclockwise
                new_state[1] = temp_state[19];   // F[1] -> U[1]
                new_state[4] = temp_state[22];   // F[4] -> U[4]
                new_state[7] = temp_state[25];   // F[7] -> U[7]
                new_state[19] = temp_state[28];  // D[1] -> F[1]
                new_state[22] = temp_state[31];  // D[4] -> F[4]
                new_state[25] = temp_state[34];  // D[7] -> F[7]
                new_state[28] = temp_state[52];  // B[7] -> D[1]
                new_state[31] = temp_state[49];  // B[4] -> D[4]
                new_state[34] = temp_state[46];  // B[1] -> D[7]
                new_state[46] = temp_state[7];   // U[7] -> B[1]
                new_state[49] = temp_state[4];   // U[4] -> B[4]
                new_state[52] = temp_state[1];   // U[1] -> B[7]
            }
            break;
        }

        case 'S': {
            if (direction == 1) {
                // S rotation clockwise (same direction as F)
                new_state[3] = temp_state[43];   // L[7] -> U[3]
                new_state[4] = temp_state[40];   // L[4] -> U[4]
                new_state[5] = temp_state[37];   // L[1] -> U[5]
                new_state[10] = temp_state[3];   // U[3] -> R[1]
                new_state[13] = temp_state[4];   // U[4] -> R[4]
                new_state[16] = temp_state[5];   // U[5] -> R[7]
                new_state[30] = temp_state[16];  // R[7] -> D[3]
                new_state[31] = temp_state[13];  // R[4] -> D[4]
                new_state[32] = temp_state[10];  // R[1] -> D[5]
                new_state[37] = temp_state[30];  // D[3] -> L[1]
                new_state[40] = temp_state[31];  // D[4] -> L[4]
                new_state[43] = temp_state[32];  // D[5] -> L[7]
            } else if (direction == 2) {
                // S rotation 180°
                new_state[3] = temp_state[32];   // D[5] -> U[3]
                new_state[4] = temp_state[31];   // D[4] -> U[4]
                new_state[5] = temp_state[30];   // D[3] -> U[5]
                new_state[10] = temp_state[43];  // L[7] -> R[1]
                new_state[13] = temp_state[40];  // L[4] -> R[4]
                new_state[16] = temp_state[37];  // L[1] -> R[7]
                new_state[30] = temp_state[5];   // U[5] -> D[3]
                new_state[31] = temp_state[4];   // U[4] -> D[4]
                new_state[32] = temp_state[3];   // U[3] -> D[5]
                new_state[37] = temp_state[16];  // R[7] -> L[1]
                new_state[40] = temp_state[13];  // R[4] -> L[4]
                new_state[43] = temp_state[10];  // R[1] -> L[7]
            } else { // direction == 3 (counterclockwise)
                // S rotation counterclockwise
                new_state[3] = temp_state[10];   // R[1] -> U[3]
                new_state[4] = temp_state[13];   // R[4] -> U[4]
                new_state[5] = temp_state[16];   // R[7] -> U[5]
                new_state[10] = temp_state[32];  // D[5] -> R[1]
                new_state[13] = temp_state[31];  // D[4] -> R[4]
                new_state[16] = temp_state[30];  // D[3] -> R[7]
                new_state[30] = temp_state[37];  // L[1] -> D[3]
                new_state[31] = temp_state[40];  // L[4] -> D[4]
                new_state[32] = temp_state[43];  // L[7] -> D[5]
                new_state[37] = temp_state[5];   // U[5] -> L[1]
                new_state[40] = temp_state[4];   // U[4] -> L[4]
                new_state[43] = temp_state[3];   // U[3] -> L[7]
            }
            break;
        }

        case 'E': {
            if (direction == 1) {
                // E rotation clockwise (same direction as D)
                new_state[21] = temp_state[39];  // L[3] -> F[3]
                new_state[22] = temp_state[40];  // L[4] -> F[4]
                new_state[23] = temp_state[41];  // L[5] -> F[5]
                new_state[12] = temp_state[21];  // F[3] -> R[3]
                new_state[13] = temp_state[22];  // F[4] -> R[4]
                new_state[14] = temp_state[23];  // F[5] -> R[5]
                new_state[48] = temp_state[12];  // R[3] -> B[3]
                new_state[49] = temp_state[13];  // R[4] -> B[4]
                new_state[50] = temp_state[14];  // R[5] -> B[5]
                new_state[39] = temp_state[48];  // B[3] -> L[3]
                new_state[40] = temp_state[49];  // B[4] -> L[4]
                new_state[41] = temp_state[50];  // B[5] -> L[5]
            } else if (direction == 2) {
                // E rotation 180°
                new_state[21] = temp_state[48];  // B[3] -> F[3]
                new_state[22] = temp_state[49];  // B[4] -> F[4]
                new_state[23] = temp_state[50];  // B[5] -> F[5]
                new_state[12] = temp_state[39];  // L[3] -> R[3]
                new_state[13] = temp_state[40];  // L[4] -> R[4]
                new_state[14] = temp_state[41];  // L[5] -> R[5]
                new_state[48] = temp_state[21];  // F[3] -> B[3]
                new_state[49] = temp_state[22];  // F[4] -> B[4]
                new_state[50] = temp_state[23];  // F[5] -> B[5]
                new_state[39] = temp_state[12];  // R[3] -> L[3]
                new_state[40] = temp_state[13];  // R[4] -> L[4]
                new_state[41] = temp_state[14];  // R[5] -> L[5]
            } else { // direction == 3 (counterclockwise)
                // E rotation counterclockwise
                new_state[21] = temp_state[12];  // R[3] -> F[3]
                new_state[22] = temp_state[13];  // R[4] -> F[4]
                new_state[23] = temp_state[14];  // R[5] -> F[5]
                new_state[12] = temp_state[48];  // B[3] -> R[3]
                new_state[13] = temp_state[49];  // B[4] -> R[4]
                new_state[14] = temp_state[50];  // B[5] -> R[5]
                new_state[48] = temp_state[39];  // L[3] -> B[3]
                new_state[49] = temp_state[40];  // L[4] -> B[4]
                new_state[50] = temp_state[41];  // L[5] -> B[5]
                new_state[39] = temp_state[21];  // F[3] -> L[3]
                new_state[40] = temp_state[22];  // F[4] -> L[4]
                new_state[41] = temp_state[23];  // F[5] -> L[5]
            }
            break;
        }

        case 'x': {
            if (direction == 1) {
                // x rotation: U<-F, R clockwise, F<-D, D<-B(inverted), L counter-clockwise, B<-U(inverted)

                // U <- F (direct copy)
                new_state[0] = temp_state[18];   // F[0] -> U[0] (position 18 -> 0)
                new_state[1] = temp_state[19];   // F[1] -> U[1] (position 19 -> 1)
                new_state[2] = temp_state[20];   // F[2] -> U[2] (position 20 -> 2)
                new_state[3] = temp_state[21];   // F[3] -> U[3] (position 21 -> 3)
                new_state[4] = temp_state[22];   // F[4] -> U[4] (position 22 -> 4)
                new_state[5] = temp_state[23];   // F[5] -> U[5] (position 23 -> 5)
                new_state[6] = temp_state[24];   // F[6] -> U[6] (position 24 -> 6)
                new_state[7] = temp_state[25];   // F[7] -> U[7] (position 25 -> 7)
                new_state[8] = temp_state[26];   // F[8] -> U[8] (position 26 -> 8)

                // R rotates clockwise
                new_state[9] = temp_state[15];   // R[6] -> R[0] (position 15 -> 9)
                new_state[10] = temp_state[12];  // R[3] -> R[1] (position 12 -> 10)
                new_state[11] = temp_state[9];   // R[0] -> R[2] (position 9 -> 11)
                new_state[12] = temp_state[16];  // R[7] -> R[3] (position 16 -> 12)
                new_state[13] = temp_state[13];  // R[4] -> R[4] (position 13 -> 13)
                new_state[14] = temp_state[10];  // R[1] -> R[5] (position 10 -> 14)
                new_state[15] = temp_state[17];  // R[8] -> R[6] (position 17 -> 15)
                new_state[16] = temp_state[14];  // R[5] -> R[7] (position 14 -> 16)
                new_state[17] = temp_state[11];  // R[2] -> R[8] (position 11 -> 17)

                // F <- D (direct copy)
                new_state[18] = temp_state[27];  // D[0] -> F[0] (position 27 -> 18)
                new_state[19] = temp_state[28];  // D[1] -> F[1] (position 28 -> 19)
                new_state[20] = temp_state[29];  // D[2] -> F[2] (position 29 -> 20)
                new_state[21] = temp_state[30];  // D[3] -> F[3] (position 30 -> 21)
                new_state[22] = temp_state[31];  // D[4] -> F[4] (position 31 -> 22)
                new_state[23] = temp_state[32];  // D[5] -> F[5] (position 32 -> 23)
                new_state[24] = temp_state[33];  // D[6] -> F[6] (position 33 -> 24)
                new_state[25] = temp_state[34];  // D[7] -> F[7] (position 34 -> 25)
                new_state[26] = temp_state[35];  // D[8] -> F[8] (position 35 -> 26)

                // D <- B (inverted)
                new_state[27] = temp_state[53];  // B[8] -> D[0] (position 53 -> 27)
                new_state[28] = temp_state[52];  // B[7] -> D[1] (position 52 -> 28)
                new_state[29] = temp_state[51];  // B[6] -> D[2] (position 51 -> 29)
                new_state[30] = temp_state[50];  // B[5] -> D[3] (position 50 -> 30)
                new_state[31] = temp_state[49];  // B[4] -> D[4] (position 49 -> 31)
                new_state[32] = temp_state[48];  // B[3] -> D[5] (position 48 -> 32)
                new_state[33] = temp_state[47];  // B[2] -> D[6] (position 47 -> 33)
                new_state[34] = temp_state[46];  // B[1] -> D[7] (position 46 -> 34)
                new_state[35] = temp_state[45];  // B[0] -> D[8] (position 45 -> 35)

                // L rotates counter-clockwise
                new_state[36] = temp_state[38];  // L[2] -> L[0] (position 38 -> 36)
                new_state[37] = temp_state[41];  // L[5] -> L[1] (position 41 -> 37)
                new_state[38] = temp_state[44];  // L[8] -> L[2] (position 44 -> 38)
                new_state[39] = temp_state[37];  // L[1] -> L[3] (position 37 -> 39)
                new_state[40] = temp_state[40];  // L[4] -> L[4] (position 40 -> 40)
                new_state[41] = temp_state[43];  // L[7] -> L[5] (position 43 -> 41)
                new_state[42] = temp_state[36];  // L[0] -> L[6] (position 36 -> 42)
                new_state[43] = temp_state[39];  // L[3] -> L[7] (position 39 -> 43)
                new_state[44] = temp_state[42];  // L[6] -> L[8] (position 42 -> 44)

                // B <- U (inverted)
                new_state[45] = temp_state[8];   // U[8] -> B[0] (position 8 -> 45)
                new_state[46] = temp_state[7];   // U[7] -> B[1] (position 7 -> 46)
                new_state[47] = temp_state[6];   // U[6] -> B[2] (position 6 -> 47)
                new_state[48] = temp_state[5];   // U[5] -> B[3] (position 5 -> 48)
                new_state[49] = temp_state[4];   // U[4] -> B[4] (position 4 -> 49)
                new_state[50] = temp_state[3];   // U[3] -> B[5] (position 3 -> 50)
                new_state[51] = temp_state[2];   // U[2] -> B[6] (position 2 -> 51)
                new_state[52] = temp_state[1];   // U[1] -> B[7] (position 1 -> 52)
                new_state[53] = temp_state[0];   // U[0] -> B[8] (position 0 -> 53)
            } else if (direction == 2) {
                // x2 rotation: U<-D, R 180°, F<-B(inverted), D<-U, L 180°, B<-F(inverted)

                // U <- D (direct copy)
                new_state[0] = temp_state[27];   // D[0] -> U[0] (position 27 -> 0)
                new_state[1] = temp_state[28];   // D[1] -> U[1] (position 28 -> 1)
                new_state[2] = temp_state[29];   // D[2] -> U[2] (position 29 -> 2)
                new_state[3] = temp_state[30];   // D[3] -> U[3] (position 30 -> 3)
                new_state[4] = temp_state[31];   // D[4] -> U[4] (position 31 -> 4)
                new_state[5] = temp_state[32];   // D[5] -> U[5] (position 32 -> 5)
                new_state[6] = temp_state[33];   // D[6] -> U[6] (position 33 -> 6)
                new_state[7] = temp_state[34];   // D[7] -> U[7] (position 34 -> 7)
                new_state[8] = temp_state[35];   // D[8] -> U[8] (position 35 -> 8)

                // R rotates 180°
                new_state[9] = temp_state[17];   // R[8] -> R[0] (position 17 -> 9)
                new_state[10] = temp_state[16];  // R[7] -> R[1] (position 16 -> 10)
                new_state[11] = temp_state[15];  // R[6] -> R[2] (position 15 -> 11)
                new_state[12] = temp_state[14];  // R[5] -> R[3] (position 14 -> 12)
                new_state[13] = temp_state[13];  // R[4] -> R[4] (position 13 -> 13)
                new_state[14] = temp_state[12];  // R[3] -> R[5] (position 12 -> 14)
                new_state[15] = temp_state[11];  // R[2] -> R[6] (position 11 -> 15)
                new_state[16] = temp_state[10];  // R[1] -> R[7] (position 10 -> 16)
                new_state[17] = temp_state[9];   // R[0] -> R[8] (position 9 -> 17)

                // F <- B (inverted)
                new_state[18] = temp_state[53];  // B[8] -> F[0] (position 53 -> 18)
                new_state[19] = temp_state[52];  // B[7] -> F[1] (position 52 -> 19)
                new_state[20] = temp_state[51];  // B[6] -> F[2] (position 51 -> 20)
                new_state[21] = temp_state[50];  // B[5] -> F[3] (position 50 -> 21)
                new_state[22] = temp_state[49];  // B[4] -> F[4] (position 49 -> 22)
                new_state[23] = temp_state[48];  // B[3] -> F[5] (position 48 -> 23)
                new_state[24] = temp_state[47];  // B[2] -> F[6] (position 47 -> 24)
                new_state[25] = temp_state[46];  // B[1] -> F[7] (position 46 -> 25)
                new_state[26] = temp_state[45];  // B[0] -> F[8] (position 45 -> 26)

                // D <- U (direct copy)
                new_state[27] = temp_state[0];   // U[0] -> D[0] (position 0 -> 27)
                new_state[28] = temp_state[1];   // U[1] -> D[1] (position 1 -> 28)
                new_state[29] = temp_state[2];   // U[2] -> D[2] (position 2 -> 29)
                new_state[30] = temp_state[3];   // U[3] -> D[3] (position 3 -> 30)
                new_state[31] = temp_state[4];   // U[4] -> D[4] (position 4 -> 31)
                new_state[32] = temp_state[5];   // U[5] -> D[5] (position 5 -> 32)
                new_state[33] = temp_state[6];   // U[6] -> D[6] (position 6 -> 33)
                new_state[34] = temp_state[7];   // U[7] -> D[7] (position 7 -> 34)
                new_state[35] = temp_state[8];   // U[8] -> D[8] (position 8 -> 35)

                // L rotates 180°
                new_state[36] = temp_state[44];  // L[8] -> L[0] (position 44 -> 36)
                new_state[37] = temp_state[43];  // L[7] -> L[1] (position 43 -> 37)
                new_state[38] = temp_state[42];  // L[6] -> L[2] (position 42 -> 38)
                new_state[39] = temp_state[41];  // L[5] -> L[3] (position 41 -> 39)
                new_state[40] = temp_state[40];  // L[4] -> L[4] (position 40 -> 40)
                new_state[41] = temp_state[39];  // L[3] -> L[5] (position 39 -> 41)
                new_state[42] = temp_state[38];  // L[2] -> L[6] (position 38 -> 42)
                new_state[43] = temp_state[37];  // L[1] -> L[7] (position 37 -> 43)
                new_state[44] = temp_state[36];  // L[0] -> L[8] (position 36 -> 44)

                // B <- F (inverted)
                new_state[45] = temp_state[26];  // F[8] -> B[0] (position 26 -> 45)
                new_state[46] = temp_state[25];  // F[7] -> B[1] (position 25 -> 46)
                new_state[47] = temp_state[24];  // F[6] -> B[2] (position 24 -> 47)
                new_state[48] = temp_state[23];  // F[5] -> B[3] (position 23 -> 48)
                new_state[49] = temp_state[22];  // F[4] -> B[4] (position 22 -> 49)
                new_state[50] = temp_state[21];  // F[3] -> B[5] (position 21 -> 50)
                new_state[51] = temp_state[20];  // F[2] -> B[6] (position 20 -> 51)
                new_state[52] = temp_state[19];  // F[1] -> B[7] (position 19 -> 52)
                new_state[53] = temp_state[18];  // F[0] -> B[8] (position 18 -> 53)
            } else {
                // x' rotation: U<-B(inverted), R counter-clockwise, F<-U, D<-F, L clockwise, B<-D(inverted)

                // U <- B (inverted)
                new_state[0] = temp_state[53];   // B[8] -> U[0] (position 53 -> 0)
                new_state[1] = temp_state[52];   // B[7] -> U[1] (position 52 -> 1)
                new_state[2] = temp_state[51];   // B[6] -> U[2] (position 51 -> 2)
                new_state[3] = temp_state[50];   // B[5] -> U[3] (position 50 -> 3)
                new_state[4] = temp_state[49];   // B[4] -> U[4] (position 49 -> 4)
                new_state[5] = temp_state[48];   // B[3] -> U[5] (position 48 -> 5)
                new_state[6] = temp_state[47];   // B[2] -> U[6] (position 47 -> 6)
                new_state[7] = temp_state[46];   // B[1] -> U[7] (position 46 -> 7)
                new_state[8] = temp_state[45];   // B[0] -> U[8] (position 45 -> 8)

                // R rotates counter-clockwise
                new_state[9] = temp_state[11];   // R[2] -> R[0] (position 11 -> 9)
                new_state[10] = temp_state[14];  // R[5] -> R[1] (position 14 -> 10)
                new_state[11] = temp_state[17];  // R[8] -> R[2] (position 17 -> 11)
                new_state[12] = temp_state[10];  // R[1] -> R[3] (position 10 -> 12)
                new_state[13] = temp_state[13];  // R[4] -> R[4] (position 13 -> 13)
                new_state[14] = temp_state[16];  // R[7] -> R[5] (position 16 -> 14)
                new_state[15] = temp_state[9];   // R[0] -> R[6] (position 9 -> 15)
                new_state[16] = temp_state[12];  // R[3] -> R[7] (position 12 -> 16)
                new_state[17] = temp_state[15];  // R[6] -> R[8] (position 15 -> 17)

                // F <- U (direct copy)
                new_state[18] = temp_state[0];   // U[0] -> F[0] (position 0 -> 18)
                new_state[19] = temp_state[1];   // U[1] -> F[1] (position 1 -> 19)
                new_state[20] = temp_state[2];   // U[2] -> F[2] (position 2 -> 20)
                new_state[21] = temp_state[3];   // U[3] -> F[3] (position 3 -> 21)
                new_state[22] = temp_state[4];   // U[4] -> F[4] (position 4 -> 22)
                new_state[23] = temp_state[5];   // U[5] -> F[5] (position 5 -> 23)
                new_state[24] = temp_state[6];   // U[6] -> F[6] (position 6 -> 24)
                new_state[25] = temp_state[7];   // U[7] -> F[7] (position 7 -> 25)
                new_state[26] = temp_state[8];   // U[8] -> F[8] (position 8 -> 26)

                // D <- F (direct copy)
                new_state[27] = temp_state[18];  // F[0] -> D[0] (position 18 -> 27)
                new_state[28] = temp_state[19];  // F[1] -> D[1] (position 19 -> 28)
                new_state[29] = temp_state[20];  // F[2] -> D[2] (position 20 -> 29)
                new_state[30] = temp_state[21];  // F[3] -> D[3] (position 21 -> 30)
                new_state[31] = temp_state[22];  // F[4] -> D[4] (position 22 -> 31)
                new_state[32] = temp_state[23];  // F[5] -> D[5] (position 23 -> 32)
                new_state[33] = temp_state[24];  // F[6] -> D[6] (position 24 -> 33)
                new_state[34] = temp_state[25];  // F[7] -> D[7] (position 25 -> 34)
                new_state[35] = temp_state[26];  // F[8] -> D[8] (position 26 -> 35)

                // L rotates clockwise
                new_state[36] = temp_state[42];  // L[6] -> L[0]
                new_state[37] = temp_state[39];  // L[3] -> L[1]
                new_state[38] = temp_state[36];  // L[0] -> L[2]
                new_state[39] = temp_state[43];  // L[7] -> L[3]
                new_state[40] = temp_state[40];  // L[4] -> L[4]
                new_state[41] = temp_state[37];  // L[1] -> L[5]
                new_state[42] = temp_state[44];  // L[8] -> L[6]
                new_state[43] = temp_state[41];  // L[5] -> L[7]
                new_state[44] = temp_state[38];  // L[2] -> L[8]

                // B <- D (inverted)
                new_state[45] = temp_state[35];  // D[8] -> B[0] (position 35 -> 45)
                new_state[46] = temp_state[34];  // D[7] -> B[1] (position 34 -> 46)
                new_state[47] = temp_state[33];  // D[6] -> B[2] (position 33 -> 47)
                new_state[48] = temp_state[32];  // D[5] -> B[3] (position 32 -> 48)
                new_state[49] = temp_state[31];  // D[4] -> B[4] (position 31 -> 49)
                new_state[50] = temp_state[30];  // D[3] -> B[5] (position 30 -> 50)
                new_state[51] = temp_state[29];  // D[2] -> B[6] (position 29 -> 51)
                new_state[52] = temp_state[28];  // D[1] -> B[7] (position 28 -> 52)
                new_state[53] = temp_state[27];  // D[0] -> B[8] (position 27 -> 53)
            }
            break;
        }

        case 'y': {
            if (direction == 1) {
                // y rotation: U clockwise, R<-B, F<-R, D counter-clockwise, L<-F, B<-L

                // U rotates clockwise
                new_state[0] = temp_state[6];   // U[6] -> U[0] (position 6 -> 0)
                new_state[1] = temp_state[3];   // U[3] -> U[1] (position 3 -> 1)
                new_state[2] = temp_state[0];   // U[0] -> U[2] (position 0 -> 2)
                new_state[3] = temp_state[7];   // U[7] -> U[3] (position 7 -> 3)
                new_state[4] = temp_state[4];   // U[4] -> U[4] (position 4 -> 4)
                new_state[5] = temp_state[1];   // U[1] -> U[5] (position 1 -> 5)
                new_state[6] = temp_state[8];   // U[8] -> U[6] (position 8 -> 6)
                new_state[7] = temp_state[5];   // U[5] -> U[7] (position 5 -> 7)
                new_state[8] = temp_state[2];   // U[2] -> U[8] (position 2 -> 8)

                // R <- B (direct copy)
                new_state[9] = temp_state[45];   // B[0] -> R[0] (position 45 -> 9)
                new_state[10] = temp_state[46];  // B[1] -> R[1] (position 46 -> 10)
                new_state[11] = temp_state[47];  // B[2] -> R[2] (position 47 -> 11)
                new_state[12] = temp_state[48];  // B[3] -> R[3] (position 48 -> 12)
                new_state[13] = temp_state[49];  // B[4] -> R[4] (position 49 -> 13)
                new_state[14] = temp_state[50];  // B[5] -> R[5] (position 50 -> 14)
                new_state[15] = temp_state[51];  // B[6] -> R[6] (position 51 -> 15)
                new_state[16] = temp_state[52];  // B[7] -> R[7] (position 52 -> 16)
                new_state[17] = temp_state[53];  // B[8] -> R[8] (position 53 -> 17)

                // F <- R (direct copy)
                new_state[18] = temp_state[9];   // R[0] -> F[0] (position 9 -> 18)
                new_state[19] = temp_state[10];  // R[1] -> F[1] (position 10 -> 19)
                new_state[20] = temp_state[11];  // R[2] -> F[2] (position 11 -> 20)
                new_state[21] = temp_state[12];  // R[3] -> F[3] (position 12 -> 21)
                new_state[22] = temp_state[13];  // R[4] -> F[4] (position 13 -> 22)
                new_state[23] = temp_state[14];  // R[5] -> F[5] (position 14 -> 23)
                new_state[24] = temp_state[15];  // R[6] -> F[6] (position 15 -> 24)
                new_state[25] = temp_state[16];  // R[7] -> F[7] (position 16 -> 25)
                new_state[26] = temp_state[17];  // R[8] -> F[8] (position 17 -> 26)

                // D rotates counter-clockwise
                new_state[27] = temp_state[29];  // D[2] -> D[0] (position 29 -> 27)
                new_state[28] = temp_state[32];  // D[5] -> D[1] (position 32 -> 28)
                new_state[29] = temp_state[35];  // D[8] -> D[2] (position 35 -> 29)
                new_state[30] = temp_state[28];  // D[1] -> D[3] (position 28 -> 30)
                new_state[31] = temp_state[31];  // D[4] -> D[4] (position 31 -> 31)
                new_state[32] = temp_state[34];  // D[7] -> D[5] (position 34 -> 32)
                new_state[33] = temp_state[27];  // D[0] -> D[6] (position 27 -> 33)
                new_state[34] = temp_state[30];  // D[3] -> D[7] (position 30 -> 34)
                new_state[35] = temp_state[33];  // D[6] -> D[8] (position 33 -> 35)

                // L <- F (direct copy)
                new_state[36] = temp_state[18];  // F[0] -> L[0] (position 18 -> 36)
                new_state[37] = temp_state[19];  // F[1] -> L[1] (position 19 -> 37)
                new_state[38] = temp_state[20];  // F[2] -> L[2] (position 20 -> 38)
                new_state[39] = temp_state[21];  // F[3] -> L[3] (position 21 -> 39)
                new_state[40] = temp_state[22];  // F[4] -> L[4] (position 22 -> 40)
                new_state[41] = temp_state[23];  // F[5] -> L[5] (position 23 -> 41)
                new_state[42] = temp_state[24];  // F[6] -> L[6] (position 24 -> 42)
                new_state[43] = temp_state[25];  // F[7] -> L[7] (position 25 -> 43)
                new_state[44] = temp_state[26];  // F[8] -> L[8] (position 26 -> 44)

                // B <- L (direct copy)
                new_state[45] = temp_state[36];  // L[0] -> B[0] (position 36 -> 45)
                new_state[46] = temp_state[37];  // L[1] -> B[1] (position 37 -> 46)
                new_state[47] = temp_state[38];  // L[2] -> B[2] (position 38 -> 47)
                new_state[48] = temp_state[39];  // L[3] -> B[3] (position 39 -> 48)
                new_state[49] = temp_state[40];  // L[4] -> B[4] (position 40 -> 49)
                new_state[50] = temp_state[41];  // L[5] -> B[5] (position 41 -> 50)
                new_state[51] = temp_state[42];  // L[6] -> B[6] (position 42 -> 51)
                new_state[52] = temp_state[43];  // L[7] -> B[7] (position 43 -> 52)
                new_state[53] = temp_state[44];  // L[8] -> B[8] (position 44 -> 53)
            } else if (direction == 2) {
                // y2 rotation: U 180°, R<-L, F<-B, D 180°, L<-R, B<-F

                // U rotates 180°
                new_state[0] = temp_state[8];   // U[8] -> U[0] (position 8 -> 0)
                new_state[1] = temp_state[7];   // U[7] -> U[1] (position 7 -> 1)
                new_state[2] = temp_state[6];   // U[6] -> U[2] (position 6 -> 2)
                new_state[3] = temp_state[5];   // U[5] -> U[3] (position 5 -> 3)
                new_state[4] = temp_state[4];   // U[4] -> U[4] (position 4 -> 4)
                new_state[5] = temp_state[3];   // U[3] -> U[5] (position 3 -> 5)
                new_state[6] = temp_state[2];   // U[2] -> U[6] (position 2 -> 6)
                new_state[7] = temp_state[1];   // U[1] -> U[7] (position 1 -> 7)
                new_state[8] = temp_state[0];   // U[0] -> U[8] (position 0 -> 8)

                // R <- L (direct copy)
                new_state[9] = temp_state[36];   // L[0] -> R[0] (position 36 -> 9)
                new_state[10] = temp_state[37];  // L[1] -> R[1] (position 37 -> 10)
                new_state[11] = temp_state[38];  // L[2] -> R[2] (position 38 -> 11)
                new_state[12] = temp_state[39];  // L[3] -> R[3] (position 39 -> 12)
                new_state[13] = temp_state[40];  // L[4] -> R[4] (position 40 -> 13)
                new_state[14] = temp_state[41];  // L[5] -> R[5] (position 41 -> 14)
                new_state[15] = temp_state[42];  // L[6] -> R[6] (position 42 -> 15)
                new_state[16] = temp_state[43];  // L[7] -> R[7] (position 43 -> 16)
                new_state[17] = temp_state[44];  // L[8] -> R[8] (position 44 -> 17)

                // F <- B (direct copy)
                new_state[18] = temp_state[45];  // B[0] -> F[0] (position 45 -> 18)
                new_state[19] = temp_state[46];  // B[1] -> F[1] (position 46 -> 19)
                new_state[20] = temp_state[47];  // B[2] -> F[2] (position 47 -> 20)
                new_state[21] = temp_state[48];  // B[3] -> F[3] (position 48 -> 21)
                new_state[22] = temp_state[49];  // B[4] -> F[4] (position 49 -> 22)
                new_state[23] = temp_state[50];  // B[5] -> F[5] (position 50 -> 23)
                new_state[24] = temp_state[51];  // B[6] -> F[6] (position 51 -> 24)
                new_state[25] = temp_state[52];  // B[7] -> F[7] (position 52 -> 25)
                new_state[26] = temp_state[53];  // B[8] -> F[8] (position 53 -> 26)

                // D rotates 180°
                new_state[27] = temp_state[35];  // D[8] -> D[0] (position 35 -> 27)
                new_state[28] = temp_state[34];  // D[7] -> D[1] (position 34 -> 28)
                new_state[29] = temp_state[33];  // D[6] -> D[2] (position 33 -> 29)
                new_state[30] = temp_state[32];  // D[5] -> D[3] (position 32 -> 30)
                new_state[31] = temp_state[31];  // D[4] -> D[4] (position 31 -> 31)
                new_state[32] = temp_state[30];  // D[3] -> D[5] (position 30 -> 32)
                new_state[33] = temp_state[29];  // D[2] -> D[6] (position 29 -> 33)
                new_state[34] = temp_state[28];  // D[1] -> D[7] (position 28 -> 34)
                new_state[35] = temp_state[27];  // D[0] -> D[8] (position 27 -> 35)

                // L <- R (direct copy)
                new_state[36] = temp_state[9];   // R[0] -> L[0] (position 9 -> 36)
                new_state[37] = temp_state[10];  // R[1] -> L[1] (position 10 -> 37)
                new_state[38] = temp_state[11];  // R[2] -> L[2] (position 11 -> 38)
                new_state[39] = temp_state[12];  // R[3] -> L[3] (position 12 -> 39)
                new_state[40] = temp_state[13];  // R[4] -> L[4] (position 13 -> 40)
                new_state[41] = temp_state[14];  // R[5] -> L[5] (position 14 -> 41)
                new_state[42] = temp_state[15];  // R[6] -> L[6] (position 15 -> 42)
                new_state[43] = temp_state[16];  // R[7] -> L[7] (position 16 -> 43)
                new_state[44] = temp_state[17];  // R[8] -> L[8] (position 17 -> 44)

                // B <- F (direct copy)
                new_state[45] = temp_state[18];  // F[0] -> B[0] (position 18 -> 45)
                new_state[46] = temp_state[19];  // F[1] -> B[1] (position 19 -> 46)
                new_state[47] = temp_state[20];  // F[2] -> B[2] (position 20 -> 47)
                new_state[48] = temp_state[21];  // F[3] -> B[3] (position 21 -> 48)
                new_state[49] = temp_state[22];  // F[4] -> B[4] (position 22 -> 49)
                new_state[50] = temp_state[23];  // F[5] -> B[5] (position 23 -> 50)
                new_state[51] = temp_state[24];  // F[6] -> B[6] (position 24 -> 51)
                new_state[52] = temp_state[25];  // F[7] -> B[7] (position 25 -> 52)
                new_state[53] = temp_state[26];  // F[8] -> B[8] (position 26 -> 53)
            } else {
                // y' rotation: U counter-clockwise, R<-F, F<-L, D clockwise, L<-B, B<-R

                // U rotates counter-clockwise
                new_state[0] = temp_state[2];   // U[2] -> U[0] (position 2 -> 0)
                new_state[1] = temp_state[5];   // U[5] -> U[1] (position 5 -> 1)
                new_state[2] = temp_state[8];   // U[8] -> U[2] (position 8 -> 2)
                new_state[3] = temp_state[1];   // U[1] -> U[3] (position 1 -> 3)
                new_state[4] = temp_state[4];   // U[4] -> U[4] (position 4 -> 4)
                new_state[5] = temp_state[7];   // U[7] -> U[5] (position 7 -> 5)
                new_state[6] = temp_state[0];   // U[0] -> U[6] (position 0 -> 6)
                new_state[7] = temp_state[3];   // U[3] -> U[7] (position 3 -> 7)
                new_state[8] = temp_state[6];   // U[6] -> U[8] (position 6 -> 8)

                // R <- F (direct copy)
                new_state[9] = temp_state[18];   // F[0] -> R[0] (position 18 -> 9)
                new_state[10] = temp_state[19];  // F[1] -> R[1] (position 19 -> 10)
                new_state[11] = temp_state[20];  // F[2] -> R[2] (position 20 -> 11)
                new_state[12] = temp_state[21];  // F[3] -> R[3] (position 21 -> 12)
                new_state[13] = temp_state[22];  // F[4] -> R[4] (position 22 -> 13)
                new_state[14] = temp_state[23];  // F[5] -> R[5] (position 23 -> 14)
                new_state[15] = temp_state[24];  // F[6] -> R[6] (position 24 -> 15)
                new_state[16] = temp_state[25];  // F[7] -> R[7] (position 25 -> 16)
                new_state[17] = temp_state[26];  // F[8] -> R[8] (position 26 -> 17)

                // F <- L (direct copy)
                new_state[18] = temp_state[36];  // L[0] -> F[0] (position 36 -> 18)
                new_state[19] = temp_state[37];  // L[1] -> F[1] (position 37 -> 19)
                new_state[20] = temp_state[38];  // L[2] -> F[2] (position 38 -> 20)
                new_state[21] = temp_state[39];  // L[3] -> F[3] (position 39 -> 21)
                new_state[22] = temp_state[40];  // L[4] -> F[4] (position 40 -> 22)
                new_state[23] = temp_state[41];  // L[5] -> F[5] (position 41 -> 23)
                new_state[24] = temp_state[42];  // L[6] -> F[6] (position 42 -> 24)
                new_state[25] = temp_state[43];  // L[7] -> F[7] (position 43 -> 25)
                new_state[26] = temp_state[44];  // L[8] -> F[8] (position 44 -> 26)

                // D rotates clockwise
                new_state[27] = temp_state[33];  // D[6] -> D[0] (position 33 -> 27)
                new_state[28] = temp_state[30];  // D[3] -> D[1] (position 30 -> 28)
                new_state[29] = temp_state[27];  // D[0] -> D[2] (position 27 -> 29)
                new_state[30] = temp_state[34];  // D[7] -> D[3] (position 34 -> 30)
                new_state[31] = temp_state[31];  // D[4] -> D[4] (position 31 -> 31)
                new_state[32] = temp_state[28];  // D[1] -> D[5] (position 28 -> 32)
                new_state[33] = temp_state[35];  // D[8] -> D[6] (position 35 -> 33)
                new_state[34] = temp_state[32];  // D[5] -> D[7] (position 32 -> 34)
                new_state[35] = temp_state[29];  // D[2] -> D[8] (position 29 -> 35)

                // L <- B (direct copy)
                new_state[36] = temp_state[45];  // B[0] -> L[0] (position 45 -> 36)
                new_state[37] = temp_state[46];  // B[1] -> L[1] (position 46 -> 37)
                new_state[38] = temp_state[47];  // B[2] -> L[2] (position 47 -> 38)
                new_state[39] = temp_state[48];  // B[3] -> L[3] (position 48 -> 39)
                new_state[40] = temp_state[49];  // B[4] -> L[4] (position 49 -> 40)
                new_state[41] = temp_state[50];  // B[5] -> L[5] (position 50 -> 41)
                new_state[42] = temp_state[51];  // B[6] -> L[6] (position 51 -> 42)
                new_state[43] = temp_state[52];  // B[7] -> L[7] (position 52 -> 43)
                new_state[44] = temp_state[53];  // B[8] -> L[8] (position 53 -> 44)

                // B <- R (direct copy)
                new_state[45] = temp_state[9];   // R[0] -> B[0] (position 9 -> 45)
                new_state[46] = temp_state[10];  // R[1] -> B[1] (position 10 -> 46)
                new_state[47] = temp_state[11];  // R[2] -> B[2] (position 11 -> 47)
                new_state[48] = temp_state[12];  // R[3] -> B[3] (position 12 -> 48)
                new_state[49] = temp_state[13];  // R[4] -> B[4] (position 13 -> 49)
                new_state[50] = temp_state[14];  // R[5] -> B[5] (position 14 -> 50)
                new_state[51] = temp_state[15];  // R[6] -> B[6] (position 15 -> 51)
                new_state[52] = temp_state[16];  // R[7] -> B[7] (position 16 -> 52)
                new_state[53] = temp_state[17];  // R[8] -> B[8] (position 17 -> 53)
            }
            break;
        }

        case 'z': {
            if (direction == 1) {
                // z rotation: U<-L, R<-U, F clockwise, D<-R, L<-D, B counter-clockwise

                // U <- L (with rotation: L positions that go to U)
                new_state[0] = temp_state[42];  // L[6] -> U[0] (position 42 -> 0)
                new_state[1] = temp_state[39];  // L[3] -> U[1] (position 39 -> 1)
                new_state[2] = temp_state[36];  // L[0] -> U[2] (position 36 -> 2)
                new_state[3] = temp_state[43];  // L[7] -> U[3] (position 43 -> 3)
                new_state[4] = temp_state[40];  // L[4] -> U[4] (position 40 -> 4)
                new_state[5] = temp_state[37];  // L[1] -> U[5] (position 37 -> 5)
                new_state[6] = temp_state[44];  // L[8] -> U[6] (position 44 -> 6)
                new_state[7] = temp_state[41];  // L[5] -> U[7] (position 41 -> 7)
                new_state[8] = temp_state[38];  // L[2] -> U[8] (position 38 -> 8)

                // R <- U (with rotation)
                new_state[9] = temp_state[6];   // U[6] -> R[0] (position 6 -> 9)
                new_state[10] = temp_state[3];  // U[3] -> R[1] (position 3 -> 10)
                new_state[11] = temp_state[0];  // U[0] -> R[2] (position 0 -> 11)
                new_state[12] = temp_state[7];  // U[7] -> R[3] (position 7 -> 12)
                new_state[13] = temp_state[4];  // U[4] -> R[4] (position 4 -> 13)
                new_state[14] = temp_state[1];  // U[1] -> R[5] (position 1 -> 14)
                new_state[15] = temp_state[8];  // U[8] -> R[6] (position 8 -> 15)
                new_state[16] = temp_state[5];  // U[5] -> R[7] (position 5 -> 16)
                new_state[17] = temp_state[2];  // U[2] -> R[8] (position 2 -> 17)

                // F rotates clockwise
                new_state[18] = temp_state[24]; // F[6] -> F[0]
                new_state[19] = temp_state[21]; // F[3] -> F[1]
                new_state[20] = temp_state[18]; // F[0] -> F[2]
                new_state[21] = temp_state[25]; // F[7] -> F[3]
                new_state[22] = temp_state[22]; // F[4] -> F[4]
                new_state[23] = temp_state[19]; // F[1] -> F[5]
                new_state[24] = temp_state[26]; // F[8] -> F[6]
                new_state[25] = temp_state[23]; // F[5] -> F[7]
                new_state[26] = temp_state[20]; // F[2] -> F[8]

                // D <- R (with rotation)
                new_state[27] = temp_state[15]; // R[6] -> D[0] (position 15 -> 27)
                new_state[28] = temp_state[12]; // R[3] -> D[1] (position 12 -> 28)
                new_state[29] = temp_state[9];  // R[0] -> D[2] (position 9 -> 29)
                new_state[30] = temp_state[16]; // R[7] -> D[3] (position 16 -> 30)
                new_state[31] = temp_state[13]; // R[4] -> D[4] (position 13 -> 31)
                new_state[32] = temp_state[10]; // R[1] -> D[5] (position 10 -> 32)
                new_state[33] = temp_state[17]; // R[8] -> D[6] (position 17 -> 33)
                new_state[34] = temp_state[14]; // R[5] -> D[7] (position 14 -> 34)
                new_state[35] = temp_state[11]; // R[2] -> D[8] (position 11 -> 35)

                // L <- D (with rotation)
                new_state[36] = temp_state[33]; // D[6] -> L[0] (position 33 -> 36)
                new_state[37] = temp_state[30]; // D[3] -> L[1] (position 30 -> 37)
                new_state[38] = temp_state[27]; // D[0] -> L[2] (position 27 -> 38)
                new_state[39] = temp_state[34]; // D[7] -> L[3] (position 34 -> 39)
                new_state[40] = temp_state[31]; // D[4] -> L[4] (position 31 -> 40)
                new_state[41] = temp_state[28]; // D[1] -> L[5] (position 28 -> 41)
                new_state[42] = temp_state[35]; // D[8] -> L[6] (position 35 -> 42)
                new_state[43] = temp_state[32]; // D[5] -> L[7] (position 32 -> 43)
                new_state[44] = temp_state[29]; // D[2] -> L[8] (position 29 -> 44)

                // B rotates counterclockwise
                new_state[45] = temp_state[47]; // B[2] -> B[0]
                new_state[46] = temp_state[50]; // B[5] -> B[1]
                new_state[47] = temp_state[53]; // B[8] -> B[2]
                new_state[48] = temp_state[46]; // B[1] -> B[3]
                new_state[49] = temp_state[49]; // B[4] -> B[4]
                new_state[50] = temp_state[52]; // B[7] -> B[5]
                new_state[51] = temp_state[45]; // B[0] -> B[6]
                new_state[52] = temp_state[48]; // B[3] -> B[7]
                new_state[53] = temp_state[51]; // B[6] -> B[8]
            } else if (direction == 2) {
                // z2 rotation: 180° rotation

                // U -> D (with 180° rotation)
                new_state[27] = temp_state[8];  // U[8] -> D[0]
                new_state[28] = temp_state[7];  // U[7] -> D[1]
                new_state[29] = temp_state[6];  // U[6] -> D[2]
                new_state[30] = temp_state[5];  // U[5] -> D[3]
                new_state[31] = temp_state[4];  // U[4] -> D[4]
                new_state[32] = temp_state[3];  // U[3] -> D[5]
                new_state[33] = temp_state[2];  // U[2] -> D[6]
                new_state[34] = temp_state[1];  // U[1] -> D[7]
                new_state[35] = temp_state[0];  // U[0] -> D[8]

                // R -> L (with 180° rotation)
                new_state[36] = temp_state[17]; // R[8] -> L[0]
                new_state[37] = temp_state[16]; // R[7] -> L[1]
                new_state[38] = temp_state[15]; // R[6] -> L[2]
                new_state[39] = temp_state[14]; // R[5] -> L[3]
                new_state[40] = temp_state[13]; // R[4] -> L[4]
                new_state[41] = temp_state[12]; // R[3] -> L[5]
                new_state[42] = temp_state[11]; // R[2] -> L[6]
                new_state[43] = temp_state[10]; // R[1] -> L[7]
                new_state[44] = temp_state[9];  // R[0] -> L[8]

                // F rotates 180°
                new_state[18] = temp_state[26]; // F[8] -> F[0]
                new_state[19] = temp_state[25]; // F[7] -> F[1]
                new_state[20] = temp_state[24]; // F[6] -> F[2]
                new_state[21] = temp_state[23]; // F[5] -> F[3]
                new_state[22] = temp_state[22]; // F[4] -> F[4]
                new_state[23] = temp_state[21]; // F[3] -> F[5]
                new_state[24] = temp_state[20]; // F[2] -> F[6]
                new_state[25] = temp_state[19]; // F[1] -> F[7]
                new_state[26] = temp_state[18]; // F[0] -> F[8]

                // D -> U (with 180° rotation)
                new_state[0] = temp_state[35];  // D[8] -> U[0]
                new_state[1] = temp_state[34];  // D[7] -> U[1]
                new_state[2] = temp_state[33];  // D[6] -> U[2]
                new_state[3] = temp_state[32];  // D[5] -> U[3]
                new_state[4] = temp_state[31];  // D[4] -> U[4]
                new_state[5] = temp_state[30];  // D[3] -> U[5]
                new_state[6] = temp_state[29];  // D[2] -> U[6]
                new_state[7] = temp_state[28];  // D[1] -> U[7]
                new_state[8] = temp_state[27];  // D[0] -> U[8]

                // L -> R (with 180° rotation)
                new_state[9] = temp_state[44];  // L[8] -> R[0]
                new_state[10] = temp_state[43]; // L[7] -> R[1]
                new_state[11] = temp_state[42]; // L[6] -> R[2]
                new_state[12] = temp_state[41]; // L[5] -> R[3]
                new_state[13] = temp_state[40]; // L[4] -> R[4]
                new_state[14] = temp_state[39]; // L[3] -> R[5]
                new_state[15] = temp_state[38]; // L[2] -> R[6]
                new_state[16] = temp_state[37]; // L[1] -> R[7]
                new_state[17] = temp_state[36]; // L[0] -> R[8]

                // B rotates 180°
                new_state[45] = temp_state[53]; // B[8] -> B[0]
                new_state[46] = temp_state[52]; // B[7] -> B[1]
                new_state[47] = temp_state[51]; // B[6] -> B[2]
                new_state[48] = temp_state[50]; // B[5] -> B[3]
                new_state[49] = temp_state[49]; // B[4] -> B[4]
                new_state[50] = temp_state[48]; // B[3] -> B[5]
                new_state[51] = temp_state[47]; // B[2] -> B[6]
                new_state[52] = temp_state[46]; // B[1] -> B[7]
                new_state[53] = temp_state[45]; // B[0] -> B[8]
            } else {
                // z' rotation: reverse of z

                // U <- R (with rotation)
                new_state[0] = temp_state[11];  // R[2] -> U[0] (position 11 -> 0)
                new_state[1] = temp_state[14];  // R[5] -> U[1] (position 14 -> 1)
                new_state[2] = temp_state[17];  // R[8] -> U[2] (position 17 -> 2)
                new_state[3] = temp_state[10];  // R[1] -> U[3] (position 10 -> 3)
                new_state[4] = temp_state[13];  // R[4] -> U[4] (position 13 -> 4)
                new_state[5] = temp_state[16];  // R[7] -> U[5] (position 16 -> 5)
                new_state[6] = temp_state[9];   // R[0] -> U[6] (position 9 -> 6)
                new_state[7] = temp_state[12];  // R[3] -> U[7] (position 12 -> 7)
                new_state[8] = temp_state[15];  // R[6] -> U[8] (position 15 -> 8)

                // R <- D (with rotation)
                new_state[9] = temp_state[29];  // D[2] -> R[0] (position 29 -> 9)
                new_state[10] = temp_state[32]; // D[5] -> R[1] (position 32 -> 10)
                new_state[11] = temp_state[35]; // D[8] -> R[2] (position 35 -> 11)
                new_state[12] = temp_state[28]; // D[1] -> R[3] (position 28 -> 12)
                new_state[13] = temp_state[31]; // D[4] -> R[4] (position 31 -> 13)
                new_state[14] = temp_state[34]; // D[7] -> R[5] (position 34 -> 14)
                new_state[15] = temp_state[27]; // D[0] -> R[6] (position 27 -> 15)
                new_state[16] = temp_state[30]; // D[3] -> R[7] (position 30 -> 16)
                new_state[17] = temp_state[33]; // D[6] -> R[8] (position 33 -> 17)

                // F rotates counterclockwise
                new_state[18] = temp_state[20]; // F[2] -> F[0]
                new_state[19] = temp_state[23]; // F[5] -> F[1]
                new_state[20] = temp_state[26]; // F[8] -> F[2]
                new_state[21] = temp_state[19]; // F[1] -> F[3]
                new_state[22] = temp_state[22]; // F[4] -> F[4]
                new_state[23] = temp_state[25]; // F[7] -> F[5]
                new_state[24] = temp_state[18]; // F[0] -> F[6]
                new_state[25] = temp_state[21]; // F[3] -> F[7]
                new_state[26] = temp_state[24]; // F[6] -> F[8]

                // D <- L (with rotation)
                new_state[27] = temp_state[38]; // L[2] -> D[0] (position 38 -> 27)
                new_state[28] = temp_state[41]; // L[5] -> D[1] (position 41 -> 28)
                new_state[29] = temp_state[44]; // L[8] -> D[2] (position 44 -> 29)
                new_state[30] = temp_state[37]; // L[1] -> D[3] (position 37 -> 30)
                new_state[31] = temp_state[40]; // L[4] -> D[4] (position 40 -> 31)
                new_state[32] = temp_state[43]; // L[7] -> D[5] (position 43 -> 32)
                new_state[33] = temp_state[36]; // L[0] -> D[6] (position 36 -> 33)
                new_state[34] = temp_state[39]; // L[3] -> D[7] (position 39 -> 34)
                new_state[35] = temp_state[42]; // L[6] -> D[8] (position 42 -> 35)

                // L <- U (with rotation)
                new_state[36] = temp_state[2];  // U[2] -> L[0] (position 2 -> 36)
                new_state[37] = temp_state[5];  // U[5] -> L[1] (position 5 -> 37)
                new_state[38] = temp_state[8];  // U[8] -> L[2] (position 8 -> 38)
                new_state[39] = temp_state[1];  // U[1] -> L[3] (position 1 -> 39)
                new_state[40] = temp_state[4];  // U[4] -> L[4] (position 4 -> 40)
                new_state[41] = temp_state[7];  // U[7] -> L[5] (position 7 -> 41)
                new_state[42] = temp_state[0];  // U[0] -> L[6] (position 0 -> 42)
                new_state[43] = temp_state[3];  // U[3] -> L[7] (position 3 -> 43)
                new_state[44] = temp_state[6];  // U[6] -> L[8] (position 6 -> 44)

                // B rotates clockwise
                new_state[45] = temp_state[51]; // B[6] -> B[0]
                new_state[46] = temp_state[48]; // B[3] -> B[1]
                new_state[47] = temp_state[45]; // B[0] -> B[2]
                new_state[48] = temp_state[52]; // B[7] -> B[3]
                new_state[49] = temp_state[49]; // B[4] -> B[4]
                new_state[50] = temp_state[46]; // B[1] -> B[5]
                new_state[51] = temp_state[53]; // B[8] -> B[6]
                new_state[52] = temp_state[50]; // B[5] -> B[7]
                new_state[53] = temp_state[47]; // B[2] -> B[8]
            }
            break;
        }

        case 'u': {
            if (direction == 1) {
                // u move - direct permutations from test file (wide move)

                // Face U turns clockwise
                new_state[0] = temp_state[6];    // U[0] = temp[6]
                new_state[1] = temp_state[3];    // U[1] = temp[3]
                new_state[2] = temp_state[0];    // U[2] = temp[0]
                new_state[3] = temp_state[7];    // U[3] = temp[7]
                new_state[5] = temp_state[1];    // U[5] = temp[1]
                new_state[6] = temp_state[8];    // U[6] = temp[8]
                new_state[7] = temp_state[5];    // U[7] = temp[5]
                new_state[8] = temp_state[2];    // U[8] = temp[2]

                // Permutations for u wide (includes middle slice)
                new_state[9] = temp_state[45];   // R[0] = B[0]
                new_state[10] = temp_state[46];  // R[1] = B[1]
                new_state[11] = temp_state[47];  // R[2] = B[2]
                new_state[12] = temp_state[48];  // R[3] = B[3]
                new_state[13] = temp_state[49];  // R[4] = B[4]
                new_state[14] = temp_state[50];  // R[5] = B[5]
                new_state[18] = temp_state[9];   // F[0] = R[0]
                new_state[19] = temp_state[10];  // F[1] = R[1]
                new_state[20] = temp_state[11];  // F[2] = R[2]
                new_state[21] = temp_state[12];  // F[3] = R[3]
                new_state[22] = temp_state[13];  // F[4] = R[4]
                new_state[23] = temp_state[14];  // F[5] = R[5]
                new_state[36] = temp_state[18];  // L[0] = F[0]
                new_state[37] = temp_state[19];  // L[1] = F[1]
                new_state[38] = temp_state[20];  // L[2] = F[2]
                new_state[39] = temp_state[21];  // L[3] = F[3]
                new_state[40] = temp_state[22];  // L[4] = F[4]
                new_state[41] = temp_state[23];  // L[5] = F[5]
                new_state[45] = temp_state[36];  // B[0] = L[0]
                new_state[46] = temp_state[37];  // B[1] = L[1]
                new_state[47] = temp_state[38];  // B[2] = L[2]
                new_state[48] = temp_state[39];  // B[3] = L[3]
                new_state[49] = temp_state[40];  // B[4] = L[4]
                new_state[50] = temp_state[41];  // B[5] = L[5]

            } else if (direction == 2) {
                // u2 move - direct permutations from test file (wide move)

                // Face U turns 180°
                new_state[0] = temp_state[8];    // U[0] = temp[8]
                new_state[1] = temp_state[7];    // U[1] = temp[7]
                new_state[2] = temp_state[6];    // U[2] = temp[6]
                new_state[3] = temp_state[5];    // U[3] = temp[5]
                new_state[5] = temp_state[3];    // U[5] = temp[3]
                new_state[6] = temp_state[2];    // U[6] = temp[2]
                new_state[7] = temp_state[1];    // U[7] = temp[1]
                new_state[8] = temp_state[0];    // U[8] = temp[0]

                // Permutations for u2 wide (includes middle slice)
                new_state[9] = temp_state[36];   // R[0] = L[0]
                new_state[10] = temp_state[37];  // R[1] = L[1]
                new_state[11] = temp_state[38];  // R[2] = L[2]
                new_state[12] = temp_state[39];  // R[3] = L[3]
                new_state[13] = temp_state[40];  // R[4] = L[4]
                new_state[14] = temp_state[41];  // R[5] = L[5]
                new_state[18] = temp_state[45];  // F[0] = B[0]
                new_state[19] = temp_state[46];  // F[1] = B[1]
                new_state[20] = temp_state[47];  // F[2] = B[2]
                new_state[21] = temp_state[48];  // F[3] = B[3]
                new_state[22] = temp_state[49];  // F[4] = B[4]
                new_state[23] = temp_state[50];  // F[5] = B[5]
                new_state[36] = temp_state[9];   // L[0] = R[0]
                new_state[37] = temp_state[10];  // L[1] = R[1]
                new_state[38] = temp_state[11];  // L[2] = R[2]
                new_state[39] = temp_state[12];  // L[3] = R[3]
                new_state[40] = temp_state[13];  // L[4] = R[4]
                new_state[41] = temp_state[14];  // L[5] = R[5]
                new_state[45] = temp_state[18];  // B[0] = F[0]
                new_state[46] = temp_state[19];  // B[1] = F[1]
                new_state[47] = temp_state[20];  // B[2] = F[2]
                new_state[48] = temp_state[21];  // B[3] = F[3]
                new_state[49] = temp_state[22];  // B[4] = F[4]
                new_state[50] = temp_state[23];  // B[5] = F[5]

            } else {
                // u' move - direct permutations from test file (wide move)

                // Face U turns counterclockwise
                new_state[0] = temp_state[2];    // U[0] = temp[2]
                new_state[1] = temp_state[5];    // U[1] = temp[5]
                new_state[2] = temp_state[8];    // U[2] = temp[8]
                new_state[3] = temp_state[1];    // U[3] = temp[1]
                new_state[5] = temp_state[7];    // U[5] = temp[7]
                new_state[6] = temp_state[0];    // U[6] = temp[0]
                new_state[7] = temp_state[3];    // U[7] = temp[3]
                new_state[8] = temp_state[6];    // U[8] = temp[6]

                // Permutations for u' wide (includes middle slice)
                new_state[9] = temp_state[18];   // R[0] = F[0]
                new_state[10] = temp_state[19];  // R[1] = F[1]
                new_state[11] = temp_state[20];  // R[2] = F[2]
                new_state[12] = temp_state[21];  // R[3] = F[3]
                new_state[13] = temp_state[22];  // R[4] = F[4]
                new_state[14] = temp_state[23];  // R[5] = F[5]
                new_state[18] = temp_state[36];  // F[0] = L[0]
                new_state[19] = temp_state[37];  // F[1] = L[1]
                new_state[20] = temp_state[38];  // F[2] = L[2]
                new_state[21] = temp_state[39];  // F[3] = L[3]
                new_state[22] = temp_state[40];  // F[4] = L[4]
                new_state[23] = temp_state[41];  // F[5] = L[5]
                new_state[36] = temp_state[45];  // L[0] = B[0]
                new_state[37] = temp_state[46];  // L[1] = B[1]
                new_state[38] = temp_state[47];  // L[2] = B[2]
                new_state[39] = temp_state[48];  // L[3] = B[3]
                new_state[40] = temp_state[49];  // L[4] = B[4]
                new_state[41] = temp_state[50];  // L[5] = B[5]
                new_state[45] = temp_state[9];   // B[0] = R[0]
                new_state[46] = temp_state[10];  // B[1] = R[1]
                new_state[47] = temp_state[11];  // B[2] = R[2]
                new_state[48] = temp_state[12];  // B[3] = R[3]
                new_state[49] = temp_state[13];  // B[4] = R[4]
                new_state[50] = temp_state[14];  // B[5] = R[5]
            }
            break;
        }

        case 'r': {
            if (direction == 1) {
                // r move - direct permutations from test file (wide move)

                // Face R turns clockwise
                new_state[9] = temp_state[15];   // R[0] = temp[15]
                new_state[10] = temp_state[12];  // R[1] = temp[12]
                new_state[11] = temp_state[9];   // R[2] = temp[9]
                new_state[12] = temp_state[16];  // R[3] = temp[16]
                new_state[14] = temp_state[10];  // R[5] = temp[10]
                new_state[15] = temp_state[17];  // R[6] = temp[17]
                new_state[16] = temp_state[14];  // R[7] = temp[14]
                new_state[17] = temp_state[11];  // R[8] = temp[11]

                // Permutations for r wide (includes middle slice)
                new_state[1] = temp_state[19];   // U[1] = F[1]
                new_state[2] = temp_state[20];   // U[2] = F[2]
                new_state[4] = temp_state[22];   // U[4] = F[4]
                new_state[5] = temp_state[23];   // U[5] = F[5]
                new_state[7] = temp_state[25];   // U[7] = F[7]
                new_state[8] = temp_state[26];   // U[8] = F[8]
                new_state[19] = temp_state[28];  // F[1] = D[1]
                new_state[20] = temp_state[29];  // F[2] = D[2]
                new_state[22] = temp_state[31];  // F[4] = D[4]
                new_state[23] = temp_state[32];  // F[5] = D[5]
                new_state[25] = temp_state[34];  // F[7] = D[7]
                new_state[26] = temp_state[35];  // F[8] = D[8]
                new_state[28] = temp_state[52];  // D[1] = B[7]
                new_state[29] = temp_state[51];  // D[2] = B[6]
                new_state[31] = temp_state[49];  // D[4] = B[4]
                new_state[32] = temp_state[48];  // D[5] = B[3]
                new_state[34] = temp_state[46];  // D[7] = B[1]
                new_state[35] = temp_state[45];  // D[8] = B[0]
                new_state[45] = temp_state[8];   // B[0] = U[8]
                new_state[46] = temp_state[7];   // B[1] = U[7]
                new_state[48] = temp_state[5];   // B[3] = U[5]
                new_state[49] = temp_state[4];   // B[4] = U[4]
                new_state[51] = temp_state[2];   // B[6] = U[2]
                new_state[52] = temp_state[1];   // B[7] = U[1]

            } else if (direction == 2) {
                // r2 move - direct permutations from test file (wide move)

                // Face R turns 180°
                new_state[9] = temp_state[17];   // R[0] = temp[17]
                new_state[10] = temp_state[16];  // R[1] = temp[16]
                new_state[11] = temp_state[15];  // R[2] = temp[15]
                new_state[12] = temp_state[14];  // R[3] = temp[14]
                new_state[14] = temp_state[12];  // R[5] = temp[12]
                new_state[15] = temp_state[11];  // R[6] = temp[11]
                new_state[16] = temp_state[10];  // R[7] = temp[10]
                new_state[17] = temp_state[9];   // R[8] = temp[9]

                // Permutations for r2 wide (includes middle slice)
                new_state[1] = temp_state[28];   // U[1] = D[1]
                new_state[2] = temp_state[29];   // U[2] = D[2]
                new_state[4] = temp_state[31];   // U[4] = D[4]
                new_state[5] = temp_state[32];   // U[5] = D[5]
                new_state[7] = temp_state[34];   // U[7] = D[7]
                new_state[8] = temp_state[35];   // U[8] = D[8]
                new_state[19] = temp_state[52];  // F[1] = B[7]
                new_state[20] = temp_state[51];  // F[2] = B[6]
                new_state[22] = temp_state[49];  // F[4] = B[4]
                new_state[23] = temp_state[48];  // F[5] = B[3]
                new_state[25] = temp_state[46];  // F[7] = B[1]
                new_state[26] = temp_state[45];  // F[8] = B[0]
                new_state[28] = temp_state[1];   // D[1] = U[1]
                new_state[29] = temp_state[2];   // D[2] = U[2]
                new_state[31] = temp_state[4];   // D[4] = U[4]
                new_state[32] = temp_state[5];   // D[5] = U[5]
                new_state[34] = temp_state[7];   // D[7] = U[7]
                new_state[35] = temp_state[8];   // D[8] = U[8]
                new_state[45] = temp_state[26];  // B[0] = F[8]
                new_state[46] = temp_state[25];  // B[1] = F[7]
                new_state[48] = temp_state[23];  // B[3] = F[5]
                new_state[49] = temp_state[22];  // B[4] = F[4]
                new_state[51] = temp_state[20];  // B[6] = F[2]
                new_state[52] = temp_state[19];  // B[7] = F[1]

            } else {
                // r' move - direct permutations from test file (wide move)

                // Face R turns counterclockwise
                new_state[9] = temp_state[11];   // R[0] = temp[11]
                new_state[10] = temp_state[14];  // R[1] = temp[14]
                new_state[11] = temp_state[17];  // R[2] = temp[17]
                new_state[12] = temp_state[10];  // R[3] = temp[10]
                new_state[14] = temp_state[16];  // R[5] = temp[16]
                new_state[15] = temp_state[9];   // R[6] = temp[9]
                new_state[16] = temp_state[12];  // R[7] = temp[12]
                new_state[17] = temp_state[15];  // R[8] = temp[15]

                // Permutations for r' wide (includes middle slice)
                new_state[1] = temp_state[52];   // U[1] = B[7]
                new_state[2] = temp_state[51];   // U[2] = B[6]
                new_state[4] = temp_state[49];   // U[4] = B[4]
                new_state[5] = temp_state[48];   // U[5] = B[3]
                new_state[7] = temp_state[46];   // U[7] = B[1]
                new_state[8] = temp_state[45];   // U[8] = B[0]
                new_state[19] = temp_state[1];   // F[1] = U[1]
                new_state[20] = temp_state[2];   // F[2] = U[2]
                new_state[22] = temp_state[4];   // F[4] = U[4]
                new_state[23] = temp_state[5];   // F[5] = U[5]
                new_state[25] = temp_state[7];   // F[7] = U[7]
                new_state[26] = temp_state[8];   // F[8] = U[8]
                new_state[28] = temp_state[19];  // D[1] = F[1]
                new_state[29] = temp_state[20];  // D[2] = F[2]
                new_state[31] = temp_state[22];  // D[4] = F[4]
                new_state[32] = temp_state[23];  // D[5] = F[5]
                new_state[34] = temp_state[25];  // D[7] = F[7]
                new_state[35] = temp_state[26];  // D[8] = F[8]
                new_state[45] = temp_state[35];  // B[0] = D[8]
                new_state[46] = temp_state[34];  // B[1] = D[7]
                new_state[48] = temp_state[32];  // B[3] = D[5]
                new_state[49] = temp_state[31];  // B[4] = D[4]
                new_state[51] = temp_state[29];  // B[6] = D[2]
                new_state[52] = temp_state[28];  // B[7] = D[1]
            }
            break;
        }

        case 'f': {
            if (direction == 1) {
                // f move - direct permutations from test file (wide move)

                // Face F turns clockwise
                new_state[18] = temp_state[24];  // F[0] = temp[24]
                new_state[19] = temp_state[21];  // F[1] = temp[21]
                new_state[20] = temp_state[18];  // F[2] = temp[18]
                new_state[21] = temp_state[25];  // F[3] = temp[25]
                new_state[23] = temp_state[19];  // F[5] = temp[19]
                new_state[24] = temp_state[26];  // F[6] = temp[26]
                new_state[25] = temp_state[23];  // F[7] = temp[23]
                new_state[26] = temp_state[20];  // F[8] = temp[20]

                // Permutations for f wide (includes middle slice)
                new_state[3] = temp_state[43];   // U[3] = L[7]
                new_state[4] = temp_state[40];   // U[4] = L[4]
                new_state[5] = temp_state[37];   // U[5] = L[1]
                new_state[6] = temp_state[44];   // U[6] = L[8]
                new_state[7] = temp_state[41];   // U[7] = L[5]
                new_state[8] = temp_state[38];   // U[8] = L[2]
                new_state[9] = temp_state[6];    // R[0] = U[6]
                new_state[10] = temp_state[3];   // R[1] = U[3]
                new_state[12] = temp_state[7];   // R[3] = U[7]
                new_state[13] = temp_state[4];   // R[4] = U[4]
                new_state[15] = temp_state[8];   // R[6] = U[8]
                new_state[16] = temp_state[5];   // R[7] = U[5]
                new_state[27] = temp_state[15];  // D[0] = R[6]
                new_state[28] = temp_state[12];  // D[1] = R[3]
                new_state[29] = temp_state[9];   // D[2] = R[0]
                new_state[30] = temp_state[16];  // D[3] = R[7]
                new_state[31] = temp_state[13];  // D[4] = R[4]
                new_state[32] = temp_state[10];  // D[5] = R[1]
                new_state[37] = temp_state[30];  // L[1] = D[3]
                new_state[38] = temp_state[27];  // L[2] = D[0]
                new_state[40] = temp_state[31];  // L[4] = D[4]
                new_state[41] = temp_state[28];  // L[5] = D[1]
                new_state[43] = temp_state[32];  // L[7] = D[5]
                new_state[44] = temp_state[29];  // L[8] = D[2]

            } else if (direction == 2) {
                // f2 move - direct permutations from test file (wide move)

                // Face F turns 180°
                new_state[18] = temp_state[26];  // F[0] = temp[26]
                new_state[19] = temp_state[25];  // F[1] = temp[25]
                new_state[20] = temp_state[24];  // F[2] = temp[24]
                new_state[21] = temp_state[23];  // F[3] = temp[23]
                new_state[23] = temp_state[21];  // F[5] = temp[21]
                new_state[24] = temp_state[20];  // F[6] = temp[20]
                new_state[25] = temp_state[19];  // F[7] = temp[19]
                new_state[26] = temp_state[18];  // F[8] = temp[18]

                // Permutations for f2 wide (includes middle slice)
                new_state[3] = temp_state[32];   // U[3] = D[5]
                new_state[4] = temp_state[31];   // U[4] = D[4]
                new_state[5] = temp_state[30];   // U[5] = D[3]
                new_state[6] = temp_state[29];   // U[6] = D[2]
                new_state[7] = temp_state[28];   // U[7] = D[1]
                new_state[8] = temp_state[27];   // U[8] = D[0]
                new_state[9] = temp_state[44];   // R[0] = L[8]
                new_state[10] = temp_state[43];  // R[1] = L[7]
                new_state[12] = temp_state[41];  // R[3] = L[5]
                new_state[13] = temp_state[40];  // R[4] = L[4]
                new_state[15] = temp_state[38];  // R[6] = L[2]
                new_state[16] = temp_state[37];  // R[7] = L[1]
                new_state[27] = temp_state[8];   // D[0] = U[8]
                new_state[28] = temp_state[7];   // D[1] = U[7]
                new_state[29] = temp_state[6];   // D[2] = U[6]
                new_state[30] = temp_state[5];   // D[3] = U[5]
                new_state[31] = temp_state[4];   // D[4] = U[4]
                new_state[32] = temp_state[3];   // D[5] = U[3]
                new_state[37] = temp_state[16];  // L[1] = R[7]
                new_state[38] = temp_state[15];  // L[2] = R[6]
                new_state[40] = temp_state[13];  // L[4] = R[4]
                new_state[41] = temp_state[12];  // L[5] = R[3]
                new_state[43] = temp_state[10];  // L[7] = R[1]
                new_state[44] = temp_state[9];   // L[8] = R[0]

            } else {
                // f' move - direct permutations from test file (wide move)

                // Face F turns counterclockwise
                new_state[18] = temp_state[20];  // F[0] = temp[20]
                new_state[19] = temp_state[23];  // F[1] = temp[23]
                new_state[20] = temp_state[26];  // F[2] = temp[26]
                new_state[21] = temp_state[19];  // F[3] = temp[19]
                new_state[23] = temp_state[25];  // F[5] = temp[25]
                new_state[24] = temp_state[18];  // F[6] = temp[18]
                new_state[25] = temp_state[21];  // F[7] = temp[21]
                new_state[26] = temp_state[24];  // F[8] = temp[24]

                // Permutations for f' wide (includes middle slice)
                new_state[3] = temp_state[10];   // U[3] = R[1]
                new_state[4] = temp_state[13];   // U[4] = R[4]
                new_state[5] = temp_state[16];   // U[5] = R[7]
                new_state[6] = temp_state[9];    // U[6] = R[0]
                new_state[7] = temp_state[12];   // U[7] = R[3]
                new_state[8] = temp_state[15];   // U[8] = R[6]
                new_state[9] = temp_state[29];   // R[0] = D[2]
                new_state[10] = temp_state[32];  // R[1] = D[5]
                new_state[12] = temp_state[28];  // R[3] = D[1]
                new_state[13] = temp_state[31];  // R[4] = D[4]
                new_state[15] = temp_state[27];  // R[6] = D[0]
                new_state[16] = temp_state[30];  // R[7] = D[3]
                new_state[27] = temp_state[38];  // D[0] = L[2]
                new_state[28] = temp_state[41];  // D[1] = L[5]
                new_state[29] = temp_state[44];  // D[2] = L[8]
                new_state[30] = temp_state[37];  // D[3] = L[1]
                new_state[31] = temp_state[40];  // D[4] = L[4]
                new_state[32] = temp_state[43];  // D[5] = L[7]
                new_state[37] = temp_state[5];   // L[1] = U[5]
                new_state[38] = temp_state[8];   // L[2] = U[8]
                new_state[40] = temp_state[4];   // L[4] = U[4]
                new_state[41] = temp_state[7];   // L[5] = U[7]
                new_state[43] = temp_state[3];   // L[7] = U[3]
                new_state[44] = temp_state[6];   // L[8] = U[6]
            }
            break;
        }

        case 'd': {
            if (direction == 1) {
                // d move - direct permutations from test file (wide move)

                // Face D turns clockwise
                new_state[27] = temp_state[33];  // D[0] = temp[33]
                new_state[28] = temp_state[30];  // D[1] = temp[30]
                new_state[29] = temp_state[27];  // D[2] = temp[27]
                new_state[30] = temp_state[34];  // D[3] = temp[34]
                new_state[32] = temp_state[28];  // D[5] = temp[28]
                new_state[33] = temp_state[35];  // D[6] = temp[35]
                new_state[34] = temp_state[32];  // D[7] = temp[32]
                new_state[35] = temp_state[29];  // D[8] = temp[29]

                // Permutations for d wide (includes middle slice)
                new_state[12] = temp_state[21];  // R[3] = F[3]
                new_state[13] = temp_state[22];  // R[4] = F[4]
                new_state[14] = temp_state[23];  // R[5] = F[5]
                new_state[15] = temp_state[24];  // R[6] = F[6]
                new_state[16] = temp_state[25];  // R[7] = F[7]
                new_state[17] = temp_state[26];  // R[8] = F[8]
                new_state[21] = temp_state[39];  // F[3] = L[3]
                new_state[22] = temp_state[40];  // F[4] = L[4]
                new_state[23] = temp_state[41];  // F[5] = L[5]
                new_state[24] = temp_state[42];  // F[6] = L[6]
                new_state[25] = temp_state[43];  // F[7] = L[7]
                new_state[26] = temp_state[44];  // F[8] = L[8]
                new_state[39] = temp_state[48];  // L[3] = B[3]
                new_state[40] = temp_state[49];  // L[4] = B[4]
                new_state[41] = temp_state[50];  // L[5] = B[5]
                new_state[42] = temp_state[51];  // L[6] = B[6]
                new_state[43] = temp_state[52];  // L[7] = B[7]
                new_state[44] = temp_state[53];  // L[8] = B[8]
                new_state[48] = temp_state[12];  // B[3] = R[3]
                new_state[49] = temp_state[13];  // B[4] = R[4]
                new_state[50] = temp_state[14];  // B[5] = R[5]
                new_state[51] = temp_state[15];  // B[6] = R[6]
                new_state[52] = temp_state[16];  // B[7] = R[7]
                new_state[53] = temp_state[17];  // B[8] = R[8]

            } else if (direction == 2) {
                // d2 move - direct permutations from test file (wide move)

                // Face D turns 180°
                new_state[27] = temp_state[35];  // D[0] = temp[35]
                new_state[28] = temp_state[34];  // D[1] = temp[34]
                new_state[29] = temp_state[33];  // D[2] = temp[33]
                new_state[30] = temp_state[32];  // D[3] = temp[32]
                new_state[32] = temp_state[30];  // D[5] = temp[30]
                new_state[33] = temp_state[29];  // D[6] = temp[29]
                new_state[34] = temp_state[28];  // D[7] = temp[28]
                new_state[35] = temp_state[27];  // D[8] = temp[27]

                // Permutations for d2 wide (includes middle slice)
                new_state[12] = temp_state[39];  // R[3] = L[3]
                new_state[13] = temp_state[40];  // R[4] = L[4]
                new_state[14] = temp_state[41];  // R[5] = L[5]
                new_state[15] = temp_state[42];  // R[6] = L[6]
                new_state[16] = temp_state[43];  // R[7] = L[7]
                new_state[17] = temp_state[44];  // R[8] = L[8]
                new_state[21] = temp_state[48];  // F[3] = B[3]
                new_state[22] = temp_state[49];  // F[4] = B[4]
                new_state[23] = temp_state[50];  // F[5] = B[5]
                new_state[24] = temp_state[51];  // F[6] = B[6]
                new_state[25] = temp_state[52];  // F[7] = B[7]
                new_state[26] = temp_state[53];  // F[8] = B[8]
                new_state[39] = temp_state[12];  // L[3] = R[3]
                new_state[40] = temp_state[13];  // L[4] = R[4]
                new_state[41] = temp_state[14];  // L[5] = R[5]
                new_state[42] = temp_state[15];  // L[6] = R[6]
                new_state[43] = temp_state[16];  // L[7] = R[7]
                new_state[44] = temp_state[17];  // L[8] = R[8]
                new_state[48] = temp_state[21];  // B[3] = F[3]
                new_state[49] = temp_state[22];  // B[4] = F[4]
                new_state[50] = temp_state[23];  // B[5] = F[5]
                new_state[51] = temp_state[24];  // B[6] = F[6]
                new_state[52] = temp_state[25];  // B[7] = F[7]
                new_state[53] = temp_state[26];  // B[8] = F[8]

            } else {
                // d' move - direct permutations from test file (wide move)

                // Face D turns counterclockwise
                new_state[27] = temp_state[29];  // D[0] = temp[29]
                new_state[28] = temp_state[32];  // D[1] = temp[32]
                new_state[29] = temp_state[35];  // D[2] = temp[35]
                new_state[30] = temp_state[28];  // D[3] = temp[28]
                new_state[32] = temp_state[34];  // D[5] = temp[34]
                new_state[33] = temp_state[27];  // D[6] = temp[27]
                new_state[34] = temp_state[30];  // D[7] = temp[30]
                new_state[35] = temp_state[33];  // D[8] = temp[33]

                // Permutations for d' wide (includes middle slice)
                new_state[12] = temp_state[48];  // R[3] = B[3]
                new_state[13] = temp_state[49];  // R[4] = B[4]
                new_state[14] = temp_state[50];  // R[5] = B[5]
                new_state[15] = temp_state[51];  // R[6] = B[6]
                new_state[16] = temp_state[52];  // R[7] = B[7]
                new_state[17] = temp_state[53];  // R[8] = B[8]
                new_state[21] = temp_state[12];  // F[3] = R[3]
                new_state[22] = temp_state[13];  // F[4] = R[4]
                new_state[23] = temp_state[14];  // F[5] = R[5]
                new_state[24] = temp_state[15];  // F[6] = R[6]
                new_state[25] = temp_state[16];  // F[7] = R[7]
                new_state[26] = temp_state[17];  // F[8] = R[8]
                new_state[39] = temp_state[21];  // L[3] = F[3]
                new_state[40] = temp_state[22];  // L[4] = F[4]
                new_state[41] = temp_state[23];  // L[5] = F[5]
                new_state[42] = temp_state[24];  // L[6] = F[6]
                new_state[43] = temp_state[25];  // L[7] = F[7]
                new_state[44] = temp_state[26];  // L[8] = F[8]
                new_state[48] = temp_state[39];  // B[3] = L[3]
                new_state[49] = temp_state[40];  // B[4] = L[4]
                new_state[50] = temp_state[41];  // B[5] = L[5]
                new_state[51] = temp_state[42];  // B[6] = L[6]
                new_state[52] = temp_state[43];  // B[7] = L[7]
                new_state[53] = temp_state[44];  // B[8] = L[8]
            }
            break;
        }

        case 'l': {
            if (direction == 1) {
                // l move - direct permutations from test file (wide move)

                // Face L turns clockwise
                new_state[36] = temp_state[42];  // L[0] = temp[42]
                new_state[37] = temp_state[39];  // L[1] = temp[39]
                new_state[38] = temp_state[36];  // L[2] = temp[36]
                new_state[39] = temp_state[43];  // L[3] = temp[43]
                new_state[41] = temp_state[37];  // L[5] = temp[37]
                new_state[42] = temp_state[44];  // L[6] = temp[44]
                new_state[43] = temp_state[41];  // L[7] = temp[41]
                new_state[44] = temp_state[38];  // L[8] = temp[38]

                // Permutations for l wide (includes middle slice)
                new_state[0] = temp_state[53];   // U[0] = B[8]
                new_state[1] = temp_state[52];   // U[1] = B[7]
                new_state[3] = temp_state[50];   // U[3] = B[5]
                new_state[4] = temp_state[49];   // U[4] = B[4]
                new_state[6] = temp_state[47];   // U[6] = B[2]
                new_state[7] = temp_state[46];   // U[7] = B[1]
                new_state[18] = temp_state[0];   // F[0] = U[0]
                new_state[19] = temp_state[1];   // F[1] = U[1]
                new_state[21] = temp_state[3];   // F[3] = U[3]
                new_state[22] = temp_state[4];   // F[4] = U[4]
                new_state[24] = temp_state[6];   // F[6] = U[6]
                new_state[25] = temp_state[7];   // F[7] = U[7]
                new_state[27] = temp_state[18];  // D[0] = F[0]
                new_state[28] = temp_state[19];  // D[1] = F[1]
                new_state[30] = temp_state[21];  // D[3] = F[3]
                new_state[31] = temp_state[22];  // D[4] = F[4]
                new_state[33] = temp_state[24];  // D[6] = F[6]
                new_state[34] = temp_state[25];  // D[7] = F[7]
                new_state[46] = temp_state[34];  // B[1] = D[7]
                new_state[47] = temp_state[33];  // B[2] = D[6]
                new_state[49] = temp_state[31];  // B[4] = D[4]
                new_state[50] = temp_state[30];  // B[5] = D[3]
                new_state[52] = temp_state[28];  // B[7] = D[1]
                new_state[53] = temp_state[27];  // B[8] = D[0]

            } else if (direction == 2) {
                // l2 move - direct permutations from test file (wide move)

                // Face L turns 180°
                new_state[36] = temp_state[44];  // L[0] = temp[44]
                new_state[37] = temp_state[43];  // L[1] = temp[43]
                new_state[38] = temp_state[42];  // L[2] = temp[42]
                new_state[39] = temp_state[41];  // L[3] = temp[41]
                new_state[41] = temp_state[39];  // L[5] = temp[39]
                new_state[42] = temp_state[38];  // L[6] = temp[38]
                new_state[43] = temp_state[37];  // L[7] = temp[37]
                new_state[44] = temp_state[36];  // L[8] = temp[36]

                // Permutations for l2 wide (includes middle slice)
                new_state[0] = temp_state[27];   // U[0] = D[0]
                new_state[1] = temp_state[28];   // U[1] = D[1]
                new_state[3] = temp_state[30];   // U[3] = D[3]
                new_state[4] = temp_state[31];   // U[4] = D[4]
                new_state[6] = temp_state[33];   // U[6] = D[6]
                new_state[7] = temp_state[34];   // U[7] = D[7]
                new_state[18] = temp_state[53];  // F[0] = B[8]
                new_state[19] = temp_state[52];  // F[1] = B[7]
                new_state[21] = temp_state[50];  // F[3] = B[5]
                new_state[22] = temp_state[49];  // F[4] = B[4]
                new_state[24] = temp_state[47];  // F[6] = B[2]
                new_state[25] = temp_state[46];  // F[7] = B[1]
                new_state[27] = temp_state[0];   // D[0] = U[0]
                new_state[28] = temp_state[1];   // D[1] = U[1]
                new_state[30] = temp_state[3];   // D[3] = U[3]
                new_state[31] = temp_state[4];   // D[4] = U[4]
                new_state[33] = temp_state[6];   // D[6] = U[6]
                new_state[34] = temp_state[7];   // D[7] = U[7]
                new_state[46] = temp_state[25];  // B[1] = F[7]
                new_state[47] = temp_state[24];  // B[2] = F[6]
                new_state[49] = temp_state[22];  // B[4] = F[4]
                new_state[50] = temp_state[21];  // B[5] = F[3]
                new_state[52] = temp_state[19];  // B[7] = F[1]
                new_state[53] = temp_state[18];  // B[8] = F[0]

            } else {
                // l' move - direct permutations from test file (wide move)

                // Face L turns counterclockwise
                new_state[36] = temp_state[38];  // L[0] = temp[38]
                new_state[37] = temp_state[41];  // L[1] = temp[41]
                new_state[38] = temp_state[44];  // L[2] = temp[44]
                new_state[39] = temp_state[37];  // L[3] = temp[37]
                new_state[41] = temp_state[43];  // L[5] = temp[43]
                new_state[42] = temp_state[36];  // L[6] = temp[36]
                new_state[43] = temp_state[39];  // L[7] = temp[39]
                new_state[44] = temp_state[42];  // L[8] = temp[42]

                // Permutations for l' wide (includes middle slice)
                new_state[0] = temp_state[18];   // U[0] = F[0]
                new_state[1] = temp_state[19];   // U[1] = F[1]
                new_state[3] = temp_state[21];   // U[3] = F[3]
                new_state[4] = temp_state[22];   // U[4] = F[4]
                new_state[6] = temp_state[24];   // U[6] = F[6]
                new_state[7] = temp_state[25];   // U[7] = F[7]
                new_state[18] = temp_state[27];  // F[0] = D[0]
                new_state[19] = temp_state[28];  // F[1] = D[1]
                new_state[21] = temp_state[30];  // F[3] = D[3]
                new_state[22] = temp_state[31];  // F[4] = D[4]
                new_state[24] = temp_state[33];  // F[6] = D[6]
                new_state[25] = temp_state[34];  // F[7] = D[7]
                new_state[27] = temp_state[53];  // D[0] = B[8]
                new_state[28] = temp_state[52];  // D[1] = B[7]
                new_state[30] = temp_state[50];  // D[3] = B[5]
                new_state[31] = temp_state[49];  // D[4] = B[4]
                new_state[33] = temp_state[47];  // D[6] = B[2]
                new_state[34] = temp_state[46];  // D[7] = B[1]
                new_state[46] = temp_state[7];   // B[1] = U[7]
                new_state[47] = temp_state[6];   // B[2] = U[6]
                new_state[49] = temp_state[4];   // B[4] = U[4]
                new_state[50] = temp_state[3];   // B[5] = U[3]
                new_state[52] = temp_state[1];   // B[7] = U[1]
                new_state[53] = temp_state[0];   // B[8] = U[0]
            }
            break;
        }

        case 'b': {
            if (direction == 1) {
                // Face B rotation clockwise
                new_state[45] = temp_state[51];  // B[6] -> B[0]
                new_state[46] = temp_state[48];  // B[3] -> B[1]
                new_state[47] = temp_state[45];  // B[0] -> B[2]
                new_state[48] = temp_state[52];  // B[7] -> B[3]
                new_state[49] = temp_state[49];  // B[4] -> B[4]
                new_state[50] = temp_state[46];  // B[1] -> B[5]
                new_state[51] = temp_state[53];  // B[8] -> B[6]
                new_state[52] = temp_state[50];  // B[5] -> B[7]
                new_state[53] = temp_state[47];  // B[2] -> B[8]

                // Back edge rotation (clockwise: U<-R, R<-D, D<-L, L<-U)
                new_state[0] = temp_state[11];   // U[0] = R[2]
                new_state[1] = temp_state[14];   // U[1] = R[5]
                new_state[2] = temp_state[17];   // U[2] = R[8]
                new_state[3] = temp_state[10];   // U[3] = R[1]
                new_state[4] = temp_state[13];   // U[4] = R[4]
                new_state[5] = temp_state[16];   // U[5] = R[7]
                new_state[10] = temp_state[32];  // R[1] = D[5]
                new_state[11] = temp_state[35];  // R[2] = D[8]
                new_state[13] = temp_state[31];  // R[4] = D[4]
                new_state[14] = temp_state[34];  // R[5] = D[7]
                new_state[16] = temp_state[30];  // R[7] = D[3]
                new_state[17] = temp_state[33];  // R[8] = D[6]
                new_state[30] = temp_state[37];  // D[3] = L[1]
                new_state[31] = temp_state[40];  // D[4] = L[4]
                new_state[32] = temp_state[43];  // D[5] = L[7]
                new_state[33] = temp_state[36];  // D[6] = L[0]
                new_state[34] = temp_state[39];  // D[7] = L[3]
                new_state[35] = temp_state[42];  // D[8] = L[6]
                new_state[36] = temp_state[2];   // L[0] = U[2]
                new_state[37] = temp_state[5];   // L[1] = U[5]
                new_state[39] = temp_state[1];   // L[3] = U[1]
                new_state[40] = temp_state[4];   // L[4] = U[4]
                new_state[42] = temp_state[0];   // L[6] = U[0]
                new_state[43] = temp_state[3];   // L[7] = U[3]
            } else if (direction == 2) {
                // Face B rotation 180°
                new_state[45] = temp_state[53];  // B[8] -> B[0]
                new_state[46] = temp_state[52];  // B[7] -> B[1]
                new_state[47] = temp_state[51];  // B[6] -> B[2]
                new_state[48] = temp_state[50];  // B[5] -> B[3]
                new_state[49] = temp_state[49];  // B[4] -> B[4]
                new_state[50] = temp_state[48];  // B[3] -> B[5]
                new_state[51] = temp_state[47];  // B[2] -> B[6]
                new_state[52] = temp_state[46];  // B[1] -> B[7]
                new_state[53] = temp_state[45];  // B[0] -> B[8]

                // 180° back edge rotation (U<-D, R<-L, D<-U, L<-R)
                new_state[0] = temp_state[35];   // U[0] = D[8]
                new_state[1] = temp_state[34];   // U[1] = D[7]
                new_state[2] = temp_state[33];   // U[2] = D[6]
                new_state[3] = temp_state[32];   // U[3] = D[5]
                new_state[4] = temp_state[31];   // U[4] = D[4]
                new_state[5] = temp_state[30];   // U[5] = D[3]
                new_state[10] = temp_state[43];  // R[1] = L[7]
                new_state[11] = temp_state[42];  // R[2] = L[6]
                new_state[13] = temp_state[40];  // R[4] = L[4]
                new_state[14] = temp_state[39];  // R[5] = L[3]
                new_state[16] = temp_state[37];  // R[7] = L[1]
                new_state[17] = temp_state[36];  // R[8] = L[0]
                new_state[30] = temp_state[5];   // D[3] = U[5]
                new_state[31] = temp_state[4];   // D[4] = U[4]
                new_state[32] = temp_state[3];   // D[5] = U[3]
                new_state[33] = temp_state[2];   // D[6] = U[2]
                new_state[34] = temp_state[1];   // D[7] = U[1]
                new_state[35] = temp_state[0];   // D[8] = U[0]
                new_state[36] = temp_state[17];  // L[0] = R[8]
                new_state[37] = temp_state[16];  // L[1] = R[7]
                new_state[39] = temp_state[14];  // L[3] = R[5]
                new_state[40] = temp_state[13];  // L[4] = R[4]
                new_state[42] = temp_state[11];  // L[6] = R[2]
                new_state[43] = temp_state[10];  // L[7] = R[1]
            } else {
                // Face B rotation counterclockwise
                new_state[45] = temp_state[47];  // B[2] -> B[0]
                new_state[46] = temp_state[50];  // B[5] -> B[1]
                new_state[47] = temp_state[53];  // B[8] -> B[2]
                new_state[48] = temp_state[46];  // B[1] -> B[3]
                new_state[49] = temp_state[49];  // B[4] -> B[4]
                new_state[50] = temp_state[52];  // B[7] -> B[5]
                new_state[51] = temp_state[45];  // B[0] -> B[6]
                new_state[52] = temp_state[48];  // B[3] -> B[7]
                new_state[53] = temp_state[51];  // B[6] -> B[8]

                // Back edge rotation (counterclockwise: U<-L, R<-U, D<-R, L<-D)
                new_state[0] = temp_state[42];   // U[0] = L[6]
                new_state[1] = temp_state[39];   // U[1] = L[3]
                new_state[2] = temp_state[36];   // U[2] = L[0]
                new_state[3] = temp_state[43];   // U[3] = L[7]
                new_state[4] = temp_state[40];   // U[4] = L[4]
                new_state[5] = temp_state[37];   // U[5] = L[1]
                new_state[10] = temp_state[3];   // R[1] = U[3]
                new_state[11] = temp_state[0];   // R[2] = U[0]
                new_state[13] = temp_state[4];   // R[4] = U[4]
                new_state[14] = temp_state[1];   // R[5] = U[1]
                new_state[16] = temp_state[5];   // R[7] = U[5]
                new_state[17] = temp_state[2];   // R[8] = U[2]
                new_state[30] = temp_state[16];  // D[3] = R[7]
                new_state[31] = temp_state[13];  // D[4] = R[4]
                new_state[32] = temp_state[10];  // D[5] = R[1]
                new_state[33] = temp_state[17];  // D[6] = R[8]
                new_state[34] = temp_state[14];  // D[7] = R[5]
                new_state[35] = temp_state[11];  // D[8] = R[2]
                new_state[36] = temp_state[33];  // L[0] = D[6]
                new_state[37] = temp_state[30];  // L[1] = D[3]
                new_state[39] = temp_state[34];  // L[3] = D[7]
                new_state[40] = temp_state[31];  // L[4] = D[4]
                new_state[42] = temp_state[35];  // L[6] = D[8]
                new_state[43] = temp_state[32];  // L[7] = D[5]
                new_state[52] = temp_state[48];  // B[7] = B[3]
                new_state[53] = temp_state[51];  // B[8] = B[6]
            }
            break;
        }

        default:
            PyErr_Format(PyExc_ValueError, "Invalid move face: '%c'", face);
            return NULL;
    }

    return PyUnicode_FromString(new_state);
}

// Module method definitions
static PyMethodDef RotateMethods[] = {
    {"rotate_move", rotate_move, METH_VARARGS, "Rotate cube state with given move"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef rotatemodule = {
    PyModuleDef_HEAD_INIT,
    "rotate",
    "Fast cube rotation operations",
    -1,
    RotateMethods
};

// Module initialization function
PyMODINIT_FUNC PyInit_rotate(void) {
    return PyModule_Create(&rotatemodule);
}
