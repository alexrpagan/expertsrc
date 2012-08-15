def generate_sequences(alphabet, length):
    """
    Generate all possible sequences having given length in alphabet
    """
    seqs = []
    if length == 1:
        for char in alphabet:
            seqs.append([char])
    elif length > 1:
        for char in alphabet:
            for seq in generate_sequences(alphabet, length - 1):
                seqs.append([char] + seq)
    return seqs

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]
