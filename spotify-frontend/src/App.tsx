import { ChakraProvider } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({});
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          {/* Add more routes here for other pages */}
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;
