import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

/**
 * [Security Expert Mode] AI PT Studio Backend
 * Separated Login and Registration to prevent ID duplication.
 */
public class WorkoutServer {
    private static final String USER_DB = "users_secure.db";
    private static final int PORT = 8080;

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);
        server.createContext("/api/login", new LoginHandler());
        server.createContext("/api/workout", new WorkoutHandler());
        server.setExecutor(null);
        System.out.println("🛡️ [Security Expert Mode] 서버가 시작되었습니다.");
        System.out.println("🔒 로그인/회원가입 분리 모드 활성화 (ID 중복 방지)");
        server.start();
    }

    private static String hashPassword(String password) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] encodedhash = digest.digest(password.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder(2 * encodedhash.length);
            for (byte b : encodedhash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    static class LoginHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            setupCORS(exchange);
            if (exchange.getRequestMethod().equalsIgnoreCase("OPTIONS")) { exchange.sendResponseHeaders(204, -1); return; }

            if (exchange.getRequestMethod().equalsIgnoreCase("POST")) {
                String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
                String decoded = new String(Base64.getDecoder().decode(body), StandardCharsets.UTF_8);
                
                // 형식: "userId:password:action"
                String[] parts = decoded.split(":");
                if (parts.length < 3) {
                    sendResponse(exchange, 400, "{\"status\":\"fail\", \"message\":\"잘못된 요청 형식\"}");
                    return;
                }

                String id = parts[0];
                String hashedPw = hashPassword(parts[1]);
                String action = parts[2];

                if ("register".equals(action)) {
                    if (isUserExist(id)) {
                        sendResponse(exchange, 409, "{\"status\":\"fail\", \"message\":\"이미 사용 중인 아이디입니다.\"}");
                    } else {
                        registerUser(id, hashedPw);
                        sendResponse(exchange, 200, "{\"status\":\"success\", \"message\":\"회원가입이 완료되었습니다! 로그인 해주세요.\"}");
                    }
                } else { // login
                    String userData = findUser(id, hashedPw);
                    if (userData != null) {
                        sendResponse(exchange, 200, "{\"status\":\"success\", \"message\":\"로그인 성공!\", \"data\":" + userData + "}");
                    } else {
                        if (isUserExist(id)) {
                            sendResponse(exchange, 401, "{\"status\":\"fail\", \"message\":\"비밀번호가 틀렸습니다.\"}");
                        } else {
                            sendResponse(exchange, 404, "{\"status\":\"fail\", \"message\":\"존재하지 않는 아이디입니다.\"}");
                        }
                    }
                }
            }
        }
    }

    static class WorkoutHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            setupCORS(exchange);
            if (exchange.getRequestMethod().equalsIgnoreCase("OPTIONS")) { exchange.sendResponseHeaders(204, -1); return; }

            if (exchange.getRequestMethod().equalsIgnoreCase("POST")) {
                String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
                String decoded = new String(Base64.getDecoder().decode(body), StandardCharsets.UTF_8);
                
                if (validateData(decoded)) {
                    updateUserData(decoded);
                    sendResponse(exchange, 200, "{\"status\":\"success\"}");
                } else {
                    sendResponse(exchange, 400, "{\"status\":\"error\", \"message\":\"Invalid Data\"}");
                }
            }
        }
        
        private boolean validateData(String json) {
            try {
                double avgScore = Double.parseDouble(extractValue(json, "avgScore"));
                return avgScore >= 0 && avgScore <= 100;
            } catch (Exception e) { return false; }
        }
    }

    private static synchronized String findUser(String id, String hashedPw) {
        try (BufferedReader br = new BufferedReader(new FileReader(USER_DB))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] parts = line.split("\\|");
                if (parts[0].equals(id) && parts[1].equals(hashedPw)) return parts[2];
            }
        } catch (IOException e) { }
        return null;
    }

    private static boolean isUserExist(String id) {
        try (BufferedReader br = new BufferedReader(new FileReader(USER_DB))) {
            String line;
            while ((line = br.readLine()) != null) {
                if (line.split("\\|")[0].equals(id)) return true;
            }
        } catch (IOException e) { }
        return false;
    }

    private static synchronized void registerUser(String id, String hashedPw) {
        String initialData = "{\"totalReps\":0, \"avgScore\":0.0}";
        try (PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(USER_DB, true)))) {
            out.println(id + "|" + hashedPw + "|" + initialData);
        } catch (IOException e) { e.printStackTrace(); }
    }

    private static synchronized void updateUserData(String json) {
        String id = extractValue(json, "userId");
        List<String> lines = new ArrayList<>();
        try {
            File file = new File(USER_DB);
            if (file.exists()) {
                try (BufferedReader br = new BufferedReader(new FileReader(file))) {
                    String line;
                    while ((line = br.readLine()) != null) {
                        String[] parts = line.split("\\|");
                        if (parts[0].equals(id)) {
                            lines.add(id + "|" + parts[1] + "|" + json);
                        } else {
                            lines.add(line);
                        }
                    }
                }
                try (PrintWriter pwOut = new PrintWriter(new FileWriter(USER_DB))) {
                    for (String l : lines) pwOut.println(l);
                }
            }
        } catch (IOException e) { }
    }

    private static String extractValue(String json, String key) {
        String search = "\"" + key + "\":";
        int start = json.indexOf(search) + search.length();
        if (json.charAt(start) == '\"') start++;
        int end = json.indexOf(",", start);
        if (end == -1) end = json.indexOf("}", start);
        return json.substring(start, end).replace("\"", "").trim();
    }

    private static void setupCORS(HttpExchange exchange) {
        exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().add("Access-Control-Allow-Methods", "POST, OPTIONS");
        exchange.getResponseHeaders().add("Access-Control-Allow-Headers", "Content-Type");
    }

    private static void sendResponse(HttpExchange exchange, int status, String response) throws IOException {
        byte[] bytes = response.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(status, bytes.length);
        OutputStream os = exchange.getResponseBody();
        os.write(bytes);
        os.close();
    }
}
