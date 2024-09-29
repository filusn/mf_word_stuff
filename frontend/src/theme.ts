
import createTheme from '@mui/material/styles/createTheme';

export enum OurColors {
  green = "#a8c256",
  red = "#ff5a5f",
  black = "#1b132d",
  grey = "#444554",
  white = "#dae0f2",
  turquoise = "#21a0a0",
  blue = "#669bbc",
  orange = "#ff9505"
}

// https://coolors.co/ to generate palette by locking base colors
// https://bareynol.github.io/mui-theme-creator/ to set up theme colors

export const theme = createTheme({
    components: {
      MuiTypography: {
        defaultProps: {
          color: OurColors.white
        }
      },
      // TODO: Try to overwrite this if you can (it makes url bar blue :( )
      // MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputSizeSmall css-1eywpm9-MuiInputBase-input-MuiOutlinedInput-input
    },
    palette: {
      mode: 'dark',
      background: {
        default: OurColors.black,
        paper: OurColors.black
      },
      text: {
        primary: OurColors.white,
        secondary: OurColors.grey,
      },
      primary: {
        // dark:,
        main: OurColors.white,
        // light:
        contrastText: OurColors.black
      },
      secondary: {
        // dark:
        main: OurColors.turquoise,
        // light:
        contrastText: OurColors.white
      },
      error: {
        main: OurColors.red
      },
      warning: {
        main: OurColors.orange
      },
      info: {
        main: OurColors.blue
      },
      success: {
        main: OurColors.green
      }
    }
  });
  