# File: gui_validators.py

class Validators:
    def validate_number_input(self, P): # Mengizinkan angka dan tanda minus di awal
        if P == "":
            return True
        if P == "-": # Mengizinkan input tanda minus pertama
            return True
        if P.isdigit(): # Jika hanya angka positif
            return True
        # Mengizinkan tanda minus diikuti angka (untuk angka negatif)
        if P.startswith('-') and P[1:].isdigit():
             return True
        return False
    
    def validate_positive_number_input(self, P): # Hanya mengizinkan angka positif
        if P == "":
            return True
        if P.isdigit():
            return True
        return False