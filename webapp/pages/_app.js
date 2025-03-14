import '../styles/globals.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';

BigInt.prototype.toJSON = function () {
  const int = Number.parseInt(this.toString());
  return int ?? this.toString();
};

function MyApp({Component, pageProps}) {
  const useContainer = pageProps.useContainer !== false;

  return (
    <div className="mx-auto">
      {useContainer ? (
        <div className="container mx-auto">
          <Component {...pageProps} />
        </div>
      ) : (
        <Component {...pageProps} />
      )}
    </div>
  );
}

export default MyApp
