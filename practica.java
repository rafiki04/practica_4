import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

public class practica {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Bucle para hacer peticiones continuas hasta que el usuario ingrese "n"
        while (true) {
            // Pedir al usuario que ingrese el valor de ciphertext
            System.out.print("Ingresa el valor de ciphertext: ");
            String ciphertextValue = scanner.nextLine();
            
            try {
                // La URL base sin el valor de ciphertext
                String baseUrl = "http://64.227.29.191/validador.cbc?ciphertext=";
                
                // Concatenar la URL base con el valor dinámico de ciphertext
                String urlString = baseUrl + ciphertextValue;
                
                // Crear un objeto URL a partir de la cadena de la URL
                URL url = new URL(urlString);
                
                // Abrir la conexión
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                
                // Establecer el método de solicitud como GET
                connection.setRequestMethod("GET");
                
                // Establecer un tiempo de espera de conexión
                connection.setConnectTimeout(5000);
                connection.setReadTimeout(5000);
                
                // Obtener el código de respuesta
                int responseCode = connection.getResponseCode();
                System.out.println("Código de respuesta: " + responseCode);
                
                // Leer la respuesta
                if (responseCode == HttpURLConnection.HTTP_OK) { // Si la respuesta es 200 (OK)
                    BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                    String inputLine;
                    StringBuffer response = new StringBuffer();
                    
                    while ((inputLine = in.readLine()) != null) {
                        response.append(inputLine);
                    }
                    in.close();
                    
                    // Mostrar el contenido de la respuesta
                    System.out.println("Respuesta de la página web: ");
                    System.out.println(response.toString());
                } else {
                    System.out.println("Error en la conexión.");
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
            
            // Preguntar al usuario si quiere continuar haciendo peticiones
            System.out.print("¿Quieres hacer otra petición? (n para detener): ");
            String userResponse = scanner.nextLine().toLowerCase();
            if (userResponse.equals("n")) {
                System.out.println("Programa detenido.");
                break; // Salir del bucle si el usuario ingresa "n"
            }
        }

        scanner.close(); // Cerrar el scanner al finalizar
    }
}
