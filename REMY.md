# The different models in TRELLIS

# 1 - Image conditionner ("image_cond_model")
    * DINOV2: generate latent representation per cond. image

# 2 - Sparse VAE ("sparse_structure_flow_model" & "sparse_structure_decoder")
    * First generate a noise (1, C=8, 16, 16, 16)

    * Denoise latent z_s (1,8,16,16,16)
        * This is conditioned on image tokens

    * Decode latent Decode(z_s) -> (1,1,64,64,64)

    * get vertices of positive coordinates -> (N_verts, 4) [MESH_ID, X, Y, Z]

# 3 - Structure latent ("slat_flow_model")
    * Sample noise (N_verts, 8)
    * Flow-matching (euler sampling): slat (N_verts,8)


# 4 - Decode Mesh ("slat_decoder_mesh")
    * Decode to mesh via flexicube (45 parameters /cell)
        - (N_verts, 8)
        - (N_verts, 768)
        - (N_verts*2**3, 192)
        - (N_verts*4**3, 96)
        - (N_verts*4**3, 101)
    * Upscale from 64**3 -> 256**3 3D grid
        * Each z_i now account for 4*4*4 grid

    
