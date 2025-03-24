import java.net.HttpURLConnection;
import java.net.URL;

public class atack {

    // URL del oráculo
    private static final String ORACLE_URL = "http://64.227.29.191/validador.cbc";

    // Método para verificar si el padding es válido
    private static boolean isPaddingValid(String ciphertextHex) throws Exception {
        // Crear la URL con el ciphertext
        String urlString = ORACLE_URL + "?ciphertext=" + ciphertextHex;

        // Crear la conexión HTTP
        URL url = new URL(urlString);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");

        // Leer la respuesta
        int responseCode = connection.getResponseCode();
        if (responseCode == 200) {
            String response = new String(connection.getInputStream().readAllBytes());
            return response.contains("OK");
        }
        return false;
    }

    // Método para descifrar el último bloque
    private static byte[] decryptLastBlock(byte[] ciphertext, int blockSize) throws Exception {
        byte[] decryptedBlock = new byte[blockSize];
        byte[] modifiedCiphertext = ciphertext.clone();

        // Iterar sobre cada byte del último bloque (empezando desde el final)
        for (int i = blockSize - 1; i >= 0; i--) {
            System.out.println("\nDescifrando byte " + (blockSize - i) + " del último bloque...");

            // Probar todos los valores posibles para el byte
            for (int guess = 0; guess < 256; guess++) {
                // Modificar solo el byte actual en el último bloque
                modifiedCiphertext[i] = (byte) (ciphertext[i] ^ guess ^ (blockSize - i));

                // Convertir el ciphertext modificado a hexadecimal
                String modifiedCiphertextHex = bytesToHex(modifiedCiphertext);

                // Mostrar el ciphertext modificado
                System.out.println("Intentando ciphertext: " + modifiedCiphertextHex);

                // Verificar si el padding es válido
                boolean isValid = isPaddingValid(modifiedCiphertextHex);
                System.out.println("Resultado del oráculo: " + (isValid ? "OK" : "Invalid!"));

                if (isValid) {
                    decryptedBlock[i] = (byte) (guess ^ (blockSize - i));
                    System.out.println("Byte descifrado: " + decryptedBlock[i]);
                    break;
                }
            }
        }
        return decryptedBlock;
    }

    // Método principal para descifrar el mensaje
    public static String decryptMessage(String ciphertextHex) throws Exception {
        byte[] ciphertext = hexToBytes(ciphertextHex);
        int blockSize = 16; // Tamaño de bloque para AES

        // Descifrar solo el último bloque
        System.out.println("Iniciando ataque de padding oracle en el último bloque...");
        byte[] decryptedBlock = decryptLastBlock(ciphertext, blockSize);

        // Eliminar el padding
        int paddingLength = decryptedBlock[blockSize - 1];
        byte[] finalMessage = new byte[blockSize - paddingLength];
        System.arraycopy(decryptedBlock, 0, finalMessage, 0, finalMessage.length);

        return new String(finalMessage);
    }

    // Método para convertir hexadecimal a bytes
    private static byte[] hexToBytes(String hex) {
        int len = hex.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4)
                    + Character.digit(hex.charAt(i + 1), 16));
        }
        return data;
    }

    // Método para convertir bytes a hexadecimal
    private static String bytesToHex(byte[] bytes) {
        StringBuilder hex = new StringBuilder();
        for (byte b : bytes) {
            hex.append(String.format("%02x", b));
        }
        return hex.toString();
    }

    public static void main(String[] args) {
        try {
            // Texto cifrado en hexadecimal
            String ciphertextHex = "82a6f4f7a60f9798f167bf61232d7754824d8538ded42f7e4a53915327c07456";
            System.out.println("Texto cifrado: " + ciphertextHex);
            String decryptedMessage = decryptMessage(ciphertextHex);
            System.out.println("\nMensaje descifrado: " + decryptedMessage);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}