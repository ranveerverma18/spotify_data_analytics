import { ChakraProvider } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({});
import Login from './pages/Login';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          {/* Add more routes here for dashboard and other pages */}
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;
