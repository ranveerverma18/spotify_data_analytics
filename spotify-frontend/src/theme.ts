import { extendTheme, type ThemeConfig } from '@chakra-ui/react';

const config: ThemeConfig = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
};

export const theme = extendTheme({
  config,
  colors: {
    spotify: {
      green: '#1DB954',
      black: '#191414',
      white: '#FFFFFF',
      gray: '#535353',
      lightGray: '#B3B3B3',
    },
  },
  fonts: {
    heading: '"Circular Std", -apple-system, system-ui, sans-serif',
    body: '"Circular Std", -apple-system, system-ui, sans-serif',
  },
  styles: {
    global: {
      body: {
        bg: 'spotify.black',
        color: 'spotify.white',
      },
    },
  },
  components: {
    Button: {
      variants: {
        spotify: {
          bg: 'spotify.green',
          color: 'spotify.white',
          _hover: {
            bg: '#1ed760',
            transform: 'scale(1.05)',
          },
          transition: 'all 0.2s ease-in-out',
        },
      },
    },
  },
});

export default theme; 